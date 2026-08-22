from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

def now(): return datetime.now(timezone.utc)

class Machine(Base):
    __tablename__ = "machines"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    machine_type: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(30), default="Healthy")
    health_score: Mapped[int] = mapped_column(Integer, default=100)
    risk_level: Mapped[str] = mapped_column(String(20), default="Low")
    recommendation: Mapped[str] = mapped_column(String(255), default="Machine operating normally.")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    readings = relationship("SensorReading", back_populates="machine", cascade="all,delete")
    alerts = relationship("Alert", back_populates="machine", cascade="all,delete")

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id: Mapped[int] = mapped_column(primary_key=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), index=True)
    temperature: Mapped[float | None] = mapped_column(Float, nullable=True)
    vibration: Mapped[float | None] = mapped_column(Float, nullable=True)
    pressure: Mapped[float | None] = mapped_column(Float, nullable=True)
    temperature_sensor_status: Mapped[str] = mapped_column(String(20), default="OK")
    vibration_sensor_status: Mapped[str] = mapped_column(String(20), default="OK")
    pressure_sensor_status: Mapped[str] = mapped_column(String(20), default="OK")
    anomaly_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    health_score: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(20))
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now, index=True)
    machine = relationship("Machine", back_populates="readings")

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id"), index=True)
    sensor_type: Mapped[str] = mapped_column(String(30))
    alert_type: Mapped[str] = mapped_column(String(50))
    severity: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(String(255))
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=now)
    machine = relationship("Machine", back_populates="alerts")
