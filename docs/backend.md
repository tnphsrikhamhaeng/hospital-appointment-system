# Backend Documentation

## 1. Technology
Backend ใช้ Python, FastAPI, SQLAlchemy, PostgreSQL, Alembic, Pydantic, Uvicorn และ APScheduler

## 2. Structure
~~~text
backend/app/
├── core/
├── models/
├── repositories/
├── routers/
├── schemas/
├── services/
├── utils/
└── main.py
~~~

## 3. Routers
Router ที่ถูก Register ใน main.py ได้แก่ auth, doctor, staff, department, specialization, doctor_schedule_template, appointment, appointment_qr, medical_record, profile, change_password, password_reset, notification, notification_setting, reactivate และ upload

## 4. Services
Service ใช้ประมวลผล Business Logic โดย Router จะส่งข้อมูลต่อไปยัง Service ที่เกี่ยวข้อง เช่น AppointmentService และ MedicalRecordService

## 5. Repositories
Repository ใช้จัดการการเข้าถึงข้อมูลจาก Database

## 6. Schemas
Pydantic Schema ใช้กำหนดรูปแบบ Request และ Response เช่น Login, Appointment และ Medical Record

## 7. Authentication
~~~text
POST /auth/register
POST /auth/login
POST /auth/staff-login
~~~

Backend มี Dependency สำหรับระบุ Current User และใช้ตรวจสอบสิทธิ์ใน Endpoint ที่เกี่ยวข้อง

## 8. CORS
Backend กำหนด CORS สำหรับ Origin ที่อนุญาตให้เรียก API รวมถึง Web Application ที่ Deploy แล้ว

## 9. File Upload
Backend สร้าง Directory app/uploads หากยังไม่มี และ Mount เป็น Static Files ที่ Path /uploads

## 10. Database Session
Database Session ถูกสร้างผ่าน SessionLocal และส่งให้ Endpoint ผ่าน get_db() หลัง Request เสร็จสิ้น Session จะถูกปิด
