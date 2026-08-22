from .config import PHYSICAL_BOUNDS, PRESSURE_CRITICAL, PRESSURE_NORMAL, TEMP_CRITICAL, TEMP_WARNING, VIB_CRITICAL, VIB_WARNING

def analyze(values: dict, statuses: dict, recent_anomalies: int = 0):
    failed = []
    for sensor, value in values.items():
        lo, hi = PHYSICAL_BOUNDS[sensor]
        if statuses.get(sensor) == "FAILED" or value is None or not lo <= value <= hi:
            failed.append(sensor)
    if failed:
        return 20, "Critical", "Sensor Failure", f"{failed[0].title()} sensor failure detected. Inspect sensor connection.", failed
    score, reasons = 100, []
    t, v, p = values["temperature"], values["vibration"], values["pressure"]
    if t > TEMP_CRITICAL: score -= 50; reasons.append("high temperature")
    elif t >= TEMP_WARNING: score -= 25; reasons.append("increased temperature")
    if v > VIB_CRITICAL: score -= 50; reasons.append("excessive vibration")
    elif v >= VIB_WARNING: score -= 25; reasons.append("increased vibration")
    if p < PRESSURE_CRITICAL[0] or p > PRESSURE_CRITICAL[1]: score -= 50; reasons.append("critical pressure")
    elif not PRESSURE_NORMAL[0] <= p <= PRESSURE_NORMAL[1]: score -= 25; reasons.append("abnormal pressure")
    score = max(0, score - min(recent_anomalies * 3, 15))
    if score >= 80: return score, "Low", "Healthy", "Machine operating normally.", []
    if score >= 60: return score, "Medium", "Warning", f"Inspect within 24 hours due to {', '.join(reasons)}.", []
    return score, "High", "Critical", f"Immediate inspection required due to {', '.join(reasons)}.", []
