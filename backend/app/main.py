from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routers import (
    auth,
    doctor,
    staff,
    department,
    specialization,
    doctor_schedule_template_router,
    appointment,
    appointment_qr,
    medical_record,
    profile,
    change_password,
    password_reset,
    notification,
    notification_setting,
    reactivate,
    upload,
    user_device,
)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)

app.include_router(doctor.router)

app.include_router(staff.router)

app.include_router(department.router)

app.include_router(specialization.router)

app.include_router(doctor_schedule_template_router.router)

app.include_router(appointment.router)

app.include_router(appointment_qr.router)

app.include_router(medical_record.router)

app.include_router(profile.router)

app.include_router(change_password.router)

app.include_router(password_reset.router)

app.include_router(notification.router)

app.include_router(notification_setting.router)

app.include_router(user_device.router)

app.include_router(reactivate.router)

app.include_router(upload.router)


UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads",
)