# Code Guide 06: Authentication

## 1. Authentication คืออะไร

Authentication คือกระบวนการตรวจสอบว่าผู้ใช้เป็นใคร

Backend มี Endpoint

```text
POST /auth/register
POST /auth/login
POST /auth/staff-login
```

## 2. Login Flow

```text
ผู้ใช้กรอก Username / Password
        ↓
Mobile / Web
        ↓
POST /auth/login
        ↓
Auth Router
        ↓
AuthService
        ↓
ตรวจสอบข้อมูลผู้ใช้
        ↓
ส่ง Login Response
```

## 3. Authorization

Authentication ตอบว่า

> ผู้ใช้นี้คือใคร?

Authorization ตอบว่า

> ผู้ใช้นี้มีสิทธิ์ทำอะไร?

ระบบมี Role หลัก

- PATIENT
- DOCTOR
- HOSPITAL_STAFF

ตัวอย่าง Appointment Status Endpoint ตรวจสอบ Role ก่อนอนุญาตให้ Doctor หรือ Hospital Staff เปลี่ยนสถานะ

## 4. คำถามที่ควรตอบได้

**Q: Authentication กับ Authorization ต่างกันอย่างไร?**

A: Authentication ตรวจสอบตัวตน ส่วน Authorization ตรวจสอบสิทธิ์การใช้งาน
