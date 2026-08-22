import os
os.environ["DATABASE_URL"]="sqlite:///./test_predictive.db"
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

@pytest.fixture(scope="session",autouse=True)
def database():
    Base.metadata.drop_all(engine); Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture()
def client():
    with TestClient(app) as c: yield c
