from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
import models
from routes.auth_routes   import router as auth_router
from routes.report_routes import router as report_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MediScan API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(report_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "MediScan API v2"}