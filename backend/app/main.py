from fastapi import FastAPI

from app.routers import (
  auth,
  doctor,
  department,
  specialization,
  doctor_schedule_template_router
)

app = FastAPI()

app.include_router(auth.router)
app.include_router(doctor.router)
app.include_router(department.router)
app.include_router(specialization.router)
app.include_router(doctor_schedule_template_router.router)