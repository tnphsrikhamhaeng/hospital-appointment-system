# API Documentation

Backend API พัฒนาด้วย FastAPI และแบ่ง Endpoint ตามหน้าที่ของระบบ

## 1. Authentication
~~~text
POST /auth/register
POST /auth/login
POST /auth/staff-login
~~~

## 2. Appointment
~~~text
POST   /appointments
GET    /appointments/search
GET    /appointments/my
GET    /appointments/my/schedule
GET    /appointments/{appointment_id}
GET    /appointments/{appointment_id}/patient
GET    /appointments/patients/{patient_id}
GET    /appointments/doctors/{doctor_id}
GET    /appointments/doctors/{doctor_id}/schedule
PATCH  /appointments/{appointment_id}/reschedule
PATCH  /appointments/{appointment_id}/cancel
PATCH  /appointments/{appointment_id}/status
~~~

Endpoint /appointments/my และ /appointments/my/schedule ตรวจสอบ Current User ว่าเป็น Doctor

Endpoint เปลี่ยนสถานะ Appointment อนุญาต Doctor หรือ Hospital Staff

## 3. Medical Record
~~~text
POST  /medical-records
GET   /medical-records
GET   /medical-records/doctor/history
GET   /medical-records/{medical_record_id}
PATCH /medical-records/{medical_record_id}
~~~

Medical Record มีการตรวจสอบสิทธิ์ตาม Role

## 4. Image Upload
~~~text
POST /uploads/department-image
POST /uploads/doctor-image
~~~

ใช้ Upload รูปแผนกและรูปแพทย์ โดยส่ง Request แบบ `multipart/form-data` ใน field ชื่อ `file`

รูปแบบไฟล์ที่รองรับ: JPEG, PNG และ WEBP ขนาดไม่เกิน 5 MB

เมื่ออัปโหลดสำเร็จ API ตอบกลับสถานะ HTTP `201 Created` และ JSON ที่มี `image_url` ซึ่งเป็น Secure URL จาก Cloudinary

ตัวอย่าง Response:
~~~json
{
  "image_url": "https://res.cloudinary.com/..."
}
~~~

ต้องตั้งค่า Environment Variables ของ Cloudinary ใน Backend ก่อนใช้งาน:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

ห้ามส่ง API Secret จาก Client และห้ามจัดเก็บ Secret ไว้ใน Repository

## 5. Other API Groups
ระบบยังมี Router สำหรับ Doctor, Staff, Department, Specialization, Doctor Schedule Template, Appointment QR, Profile, Change Password, Password Reset, Notification, Notification Setting และ Reactivate

## 6. Request / Response
API ใช้ Pydantic Schema สำหรับตรวจสอบและกำหนดรูปแบบ Request และ Response

## 7. API Documentation
FastAPI สร้าง Interactive API Documentation ที่ /docs เมื่อ Backend ทำงาน
