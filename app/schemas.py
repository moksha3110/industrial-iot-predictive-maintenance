from pydantic import BaseModel, ConfigDict

class ReadingCreate(BaseModel):
    machine_id: int
    temperature: float | None = None
    vibration: float | None = None
    pressure: float | None = None
    temperature_sensor_status: str = "OK"
    vibration_sensor_status: str = "OK"
    pressure_sensor_status: str = "OK"

class SimulationRequest(BaseModel):
    machine_id: int | None = None
    scenario: str = "random"

class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
