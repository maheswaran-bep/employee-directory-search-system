from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.session import engine
from app.models.employee import Base
from app.routers.employee_router import router as employee_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Employee Directory API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://localhost:3017",
],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee_router, prefix="/api/employees", tags=["Employees"])

@app.get("/")
def root():
    return {"status": "Backend running"}
