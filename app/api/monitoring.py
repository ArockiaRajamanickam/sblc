from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.infrastructure.db import SessionLocal
from app.infrastructure.metrics import metrics_endpoint
import psutil

router = APIRouter(prefix="/system", tags=["Monitoring"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/health/liveness")
def liveness():
    return {"status": "alive"}

@router.get("/health/readiness")
def readiness(db: Session = Depends(get_db)):
    try:
        # Check DB connection
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return Response(content='{"status": "not_ready", "reason": "db_connection_error"}', status_code=503)

@router.get("/metrics")
def metrics():
    return metrics_endpoint()

@router.get("/stats")
def stats():
    return {
        "cpu_usage": psutil.cpu_percent(),
        "memory_usage": psutil.virtual_memory().percent,
    }
