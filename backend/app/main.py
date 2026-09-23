from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db, engine, Base
from app.routers import auth, doctors, appointments, symptoms

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MediConnect API", version="0.1.0")

# Dev-friendly CORS. Tighten this to specific origins before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(symptoms.router)


@app.get("/")
def root():
    return {"service": "MediConnect API", "status": "running"}


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Confirms the API process is up AND that it can talk to Postgres."""
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {e}"

    return {"api": "ok", "database": db_status}
