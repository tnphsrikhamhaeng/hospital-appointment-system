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

## 9. Image Upload and Cloudinary
Backend ใช้ Cloudinary สำหรับจัดเก็บรูปภาพแทนการพึ่งพาไฟล์ใน Local Filesystem ของ Render ซึ่งอาจไม่คงอยู่หลัง Restart หรือ Deploy

Endpoints:
~~~text
POST /uploads/department-image
POST /uploads/doctor-image
~~~

ทั้งสอง Endpoint รับรูปผ่าน `multipart/form-data` ใน field `file` และส่ง Response รูปแบบ:
~~~json
{
  "image_url": "https://res.cloudinary.com/..."
}
~~~

รองรับไฟล์ JPEG, PNG และ WEBP โดยจำกัดขนาดไม่เกิน 5 MB รูปแผนกจะถูกจัดเก็บในโฟลเดอร์ Cloudinary `careflow/departments` และรูปแพทย์ใน `careflow/doctors`

Backend อ่านค่า Cloudinary จาก Environment Variables ต่อไปนี้:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

ห้ามใส่ API Secret ใน Source Code, Frontend หรือ Repository ให้กำหนดค่าผ่าน Environment ของ Backend Service บน Render แทน

เมื่ออัปโหลดสำเร็จ Backend ส่ง Secure URL กลับไปให้ Frontend ซึ่งนำ URL ไปบันทึกใน `image_url` ของข้อมูลแผนกหรือแพทย์ตามกระบวนการของระบบ

## 10. Database Session
Database Session ถูกสร้างผ่าน SessionLocal และส่งให้ Endpoint ผ่าน get_db() หลัง Request เสร็จสิ้น Session จะถูกปิด
