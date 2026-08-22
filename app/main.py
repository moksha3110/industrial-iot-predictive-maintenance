import logging
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from .config import get_settings
from .database import Base, engine, get_db
from .models import Alert, Machine, SensorReading
from .schemas import ReadingCreate, SimulationRequest
from .service import create_reading, fail_sensor, machine_dict, random_values, restore_sensor, seed

logging.basicConfig(level=get_settings().log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")

@asynccontextmanager
async def lifespan(app):
    Base.metadata.create_all(engine)
    from .database import SessionLocal
    with SessionLocal() as db: seed(db)
    logging.getLogger(__name__).info("Application started")
    yield

app = FastAPI(title="Industrial IoT Predictive Maintenance", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request): return templates.TemplateResponse(request=request, name="dashboard.html")

@app.get("/health")
def health(): return {"status":"healthy","service":"predictive-maintenance-api"}

@app.get("/api/machines")
def machines(db: Session=Depends(get_db)): return [machine_dict(db,m) for m in db.scalars(select(Machine).order_by(Machine.id)).all()]

@app.get("/api/machines/{machine_id}")
def machine(machine_id:int, db:Session=Depends(get_db)):
    m=db.get(Machine,machine_id)
    if not m: raise HTTPException(404,"Machine not found")
    return machine_dict(db,m)

@app.get("/api/machines/{machine_id}/readings")
def readings(machine_id:int, limit:int=30, db:Session=Depends(get_db)):
    if not db.get(Machine,machine_id): raise HTTPException(404,"Machine not found")
    rows=db.scalars(select(SensorReading).where(SensorReading.machine_id==machine_id).order_by(desc(SensorReading.recorded_at)).limit(min(limit,200))).all()
    return [{c.name:getattr(r,c.name) for c in SensorReading.__table__.columns} for r in reversed(rows)]

@app.get("/api/alerts")
def alerts(limit:int=50, db:Session=Depends(get_db)):
    rows=db.scalars(select(Alert).order_by(desc(Alert.created_at)).limit(min(limit,200))).all()
    return [{**{c.name:getattr(a,c.name) for c in Alert.__table__.columns},"machine_name":a.machine.name} for a in rows]

@app.get("/api/dashboard/summary")
def summary(db:Session=Depends(get_db)):
    ms=db.scalars(select(Machine)).all()
    return {"total_machines":len(ms),"healthy":sum(m.status=="Healthy" for m in ms),"warning":sum(m.status=="Warning" for m in ms),"critical":sum(m.status=="Critical" for m in ms),"sensor_failures":sum(m.status=="Sensor Failure" for m in ms),"total_alerts":db.scalar(select(func.count(Alert.id))) or 0}

@app.post("/api/simulator/readings")
def simulate_all(req:SimulationRequest, db:Session=Depends(get_db)):
    targets=[db.get(Machine,req.machine_id)] if req.machine_id else db.scalars(select(Machine)).all()
    if any(m is None for m in targets): raise HTTPException(404,"Machine not found")
    return [{"id":create_reading(db,m.id,random_values(req.scenario)).id} for m in targets]

@app.post("/api/simulator/machines/{machine_id}/reading")
def custom(machine_id:int, body:ReadingCreate, db:Session=Depends(get_db)):
    try: return {"id":create_reading(db,machine_id,body.model_dump(include={"temperature","vibration","pressure"}),{s:body.model_dump()[f"{s}_sensor_status"] for s in ("temperature","vibration","pressure")}).id}
    except LookupError as e: raise HTTPException(404,str(e))

@app.post("/api/simulator/machines/{machine_id}/failure/{sensor_type}")
def failure(machine_id:int,sensor_type:str,db:Session=Depends(get_db)):
    try: return {"reading_id":fail_sensor(db,machine_id,sensor_type).id,"status":"failure injected"}
    except LookupError as e: raise HTTPException(404,str(e))
    except ValueError as e: raise HTTPException(422,str(e))

@app.post("/api/simulator/machines/{machine_id}/restore/{sensor_type}")
def restore(machine_id:int,sensor_type:str,db:Session=Depends(get_db)):
    try: return {"reading_id":restore_sensor(db,machine_id,sensor_type).id,"status":"sensor restored"}
    except LookupError as e: raise HTTPException(404,str(e))
    except ValueError as e: raise HTTPException(422,str(e))
