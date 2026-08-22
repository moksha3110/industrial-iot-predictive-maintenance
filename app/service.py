import logging, random
from datetime import datetime, timezone
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from .analytics import analyze
from .config import VALID_SENSORS
from .models import Alert, Machine, SensorReading
from .notifications import notify_owner

log = logging.getLogger(__name__)
MACHINES = [("CNC Machine 01","CNC Machine","Assembly Hall A"),("Hydraulic Press 01","Hydraulic Press","Fabrication Bay"),("Industrial Pump 01","Centrifugal Pump","Utilities Room"),("Air Compressor 01","Rotary Compressor","Compressor House")]

def seed(db: Session):
    if db.scalar(select(func.count(Machine.id))) == 0:
        for name, kind, location in MACHINES: db.add(Machine(name=name, machine_type=kind, location=location))
        db.commit()
        for machine in db.scalars(select(Machine)).all(): create_reading(db, machine.id, random_values())

def random_values(scenario="normal"):
    values = {"temperature": round(random.uniform(42,67),1), "vibration": round(random.uniform(.8,3.5),2), "pressure": round(random.uniform(38,72),1)}
    if scenario == "high_temperature": values["temperature"] = 94.0
    elif scenario == "high_vibration": values["vibration"] = 8.8
    elif scenario == "abnormal_pressure": values["pressure"] = 104.0
    elif scenario == "random":
        scenario = random.choices(["normal","high_temperature","high_vibration","abnormal_pressure"],[.75,.08,.1,.07])[0]
        return random_values(scenario)
    return values

def create_alert(db, machine, sensor, kind, severity, message):
    alert = Alert(machine_id=machine.id, sensor_type=sensor, alert_type=kind, severity=severity, message=message)
    db.add(alert); db.commit(); db.refresh(alert)
    if kind == "Sensor Failure" or severity == "Critical": notify_owner(f"{severity}: {machine.name}", message)
    log.warning("Alert machine=%s type=%s severity=%s", machine.name, kind, severity)
    return alert

def create_reading(db: Session, machine_id: int, values: dict, statuses=None):
    machine = db.get(Machine, machine_id)
    if not machine: raise LookupError("Machine not found")
    statuses = statuses or {s: "OK" for s in VALID_SENSORS}
    score, risk, state, rec, failures = analyze(values, statuses)
    reading = SensorReading(machine_id=machine_id, temperature=values.get("temperature"), vibration=values.get("vibration"), pressure=values.get("pressure"), temperature_sensor_status=statuses.get("temperature","OK"), vibration_sensor_status=statuses.get("vibration","OK"), pressure_sensor_status=statuses.get("pressure","OK"), anomaly_detected=state != "Healthy", health_score=score, risk_level=risk)
    machine.status, machine.health_score, machine.risk_level, machine.recommendation, machine.updated_at = state, score, risk, rec, datetime.now(timezone.utc)
    db.add(reading); db.commit(); db.refresh(reading)
    for sensor in failures: create_alert(db, machine, sensor, "Sensor Failure", "Critical", f"{sensor.title()} sensor failure detected on {machine.name}. Inspect sensor connection immediately.")
    if state in {"Warning","Critical"} and not failures:
        sensor = "temperature" if values["temperature"] >= 70 else "vibration" if values["vibration"] >= 4 else "pressure"
        create_alert(db, machine, sensor, "Threshold Anomaly", "Critical" if state == "Critical" else "Warning", rec)
    return reading

def latest_values(db, machine_id):
    r = db.scalar(select(SensorReading).where(SensorReading.machine_id==machine_id).order_by(desc(SensorReading.recorded_at)))
    return {"temperature": r.temperature if r else 55, "vibration": r.vibration if r else 2, "pressure": r.pressure if r else 55}

def fail_sensor(db, machine_id, sensor):
    if sensor not in VALID_SENSORS: raise ValueError("sensor_type must be temperature, vibration, or pressure")
    values, statuses = latest_values(db, machine_id), {s:"OK" for s in VALID_SENSORS}
    values[sensor], statuses[sensor] = None, "FAILED"
    return create_reading(db, machine_id, values, statuses)

def restore_sensor(db, machine_id, sensor):
    if sensor not in VALID_SENSORS: raise ValueError("sensor_type must be temperature, vibration, or pressure")
    return create_reading(db, machine_id, random_values("normal"))

def machine_dict(db, m):
    r = db.scalar(select(SensorReading).where(SensorReading.machine_id==m.id).order_by(desc(SensorReading.recorded_at)))
    return {"id":m.id,"name":m.name,"machine_type":m.machine_type,"location":m.location,"status":m.status,"health_score":m.health_score,"risk_level":m.risk_level,"recommendation":m.recommendation,"updated_at":m.updated_at,"temperature":r.temperature if r else None,"vibration":r.vibration if r else None,"pressure":r.pressure if r else None}
