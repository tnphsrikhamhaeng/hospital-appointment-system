# Code Guide 02: Backend

## 1. Backend คืออะไร

Backend คือส่วนที่รับ Request จาก Mobile และ Web แล้วประมวลผลข้อมูลและติดต่อ Database

Backend ของ CareFlow ใช้ FastAPI

## 2. ส่วนสำคัญ

~~~text
core/
models/
repositories/
routers/
schemas/
services/
utils/
~~~

### Router

รับ API Request

### Service

ประมวลผล Business Logic

### Repository

จัดการการเข้าถึงข้อมูล

### Model

กำหนดโครงสร้างข้อมูล Database

### Schema

กำหนดรูปแบบข้อมูล Request และ Response

### Core

เก็บองค์ประกอบพื้นฐาน เช่น Database, Dependencies, Enum และ Scheduler

## 3. ตัวอย่าง Flow

~~~text
Client
 ↓
Router
 ↓
Service
 ↓
Repository
 ↓
Database
~~~

## 4. การอัปโหลดรูปด้วย Cloudinary

CareFlow ใช้ Cloudinary เก็บไฟล์รูปแผนกและรูปแพทย์บน Cloud แทนการเก็บไว้ในโฟลเดอร์ของ Backend Server

ไฟล์หลักที่เกี่ยวข้องคือ `app/routers/upload.py`

Endpoints:
~~~text
POST /uploads/department-image
POST /uploads/doctor-image
~~~

Flow การทำงาน:
~~~text
Web เลือกรูป
      ↓
ส่งไฟล์ไปยัง Backend API
      ↓
Backend ตรวจชนิดไฟล์และขนาด
      ↓
Backend อัปโหลดไฟล์ไป Cloudinary
      ↓
Cloudinary ส่ง Secure URL กลับ
      ↓
Backend ส่ง image_url กลับให้ Web
      ↓
Web บันทึก URL กับข้อมูลแผนกหรือแพทย์
~~~

ระบบรองรับ JPEG, PNG และ WEBP ขนาดไม่เกิน 5 MB ค่า Cloudinary ถูกอ่านจาก Environment Variables ของ Backend:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

API Secret ต้องเก็บไว้ที่ Backend Environment เท่านั้น ไม่ควรส่งไปยัง Web/Mobile หรือ Commit ลง GitHub

ข้อดีคือเพิ่มหรือเปลี่ยนรูปผ่านหน้า Staff ได้โดยไม่จำเป็นต้องเพิ่มไฟล์ในโปรเจกต์ Web และ Deploy Web ใหม่ทุกครั้ง

## 5. คำถามที่ควรตอบได้

**Q: FastAPI ทำหน้าที่อะไร?**

A: เป็น Framework ที่ใช้สร้าง Backend API ของระบบ

**Q: Router กับ Service ต่างกันอย่างไร?**

A: Router รับ Request และเรียก Service ส่วน Service ทำหน้าที่ประมวลผล Logic ของระบบ

**Q: ทำไมต้องแยกส่วน?**

A: เพื่อให้แต่ละส่วนมีหน้าที่ชัดเจนและจัดการโค้ดได้ง่ายขึ้น

**Q: ทำไม CareFlow ใช้ Cloudinary สำหรับรูปภาพ?**

A: เพื่อให้รูปถูกจัดเก็บบน Cloud แยกจากไฟล์ระบบของ Backend ซึ่งอาจไม่คงอยู่เมื่อ Server Restart หรือ Deploy ใหม่
