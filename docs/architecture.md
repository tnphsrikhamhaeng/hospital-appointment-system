# System Architecture

## 1. ภาพรวม
CareFlow แบ่งระบบออกเป็น 4 ส่วนหลัก ได้แก่ Mobile Application, Web Application, Backend API และ PostgreSQL Database

## 2. การเชื่อมต่อ
~~~text
Mobile Application
       │
       │ HTTP/HTTPS API
       ▼
   FastAPI Backend
       │
       ▼
 PostgreSQL Database
       ▲
       │
 Web Application
~~~

## 3. Backend Structure
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

Router รับ API Request, Service ประมวลผล Logic, Repository จัดการการเข้าถึงข้อมูล และ Model แทนโครงสร้างข้อมูล

## 4. Mobile Structure
~~~text
mobile/lib/
├── core/
├── features/
└── main.dart
~~~

## 5. Web Structure
~~~text
web/src/
├── api/
├── assets/
├── features/
├── hooks/
├── utils/
├── App.tsx
├── App.css
├── index.css
└── main.tsx
~~~

## 6. ความสัมพันธ์ข้อมูลหลัก
Appointment เชื่อมโยงกับ Patient, Doctor, Department, QR Code และ Medical Record

Medical Record เชื่อมโยงกับ Appointment, Patient และ Doctor

## 7. Scheduler
Backend เริ่ม Scheduler เมื่อ Application เริ่มทำงานผ่าน FastAPI lifespan และหยุด Scheduler เมื่อ Application หยุดทำงาน

## 8. สรุป
Client แยกจาก Backend และ Database โดย Backend เป็นศูนย์กลางสำหรับ Authentication, Authorization, Business Logic และการเข้าถึงข้อมูล
