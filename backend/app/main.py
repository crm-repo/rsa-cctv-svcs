from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="RSA CMS API",
    version="0.1.0",
    description="Backend API for RSA CMS / Mini-CRM",
)

allowed_origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "RSA CMS API is running",
        "status": "ok",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": "rsa-cms-api",
        "phase": "Phase 8 - Backend / Admin CMS / Mini-CRM",
    }