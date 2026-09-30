# Code Guide 05: Database

## 1. Database ใช้อะไร

ระบบใช้ PostgreSQL และ SQLAlchemy ORM

Alembic ใช้สำหรับ Database Migration

## 2. Flow

```text
Backend
 ↓
SQLAlchemy
 ↓
PostgreSQL
```

## 3. User

User เก็บข้อมูล เช่น username, email, password, ชื่อ, เบอร์โทรศัพท์, role และ status

Role หลัก

- PATIENT
- DOCTOR
- HOSPITAL_STAFF

## 4. Appointment

Appointment เชื่อมโยงกับ

- Patient
- Doctor
- Department
- QR Code
- Medical Record

## 5. Medical Record

Medical Record เชื่อมโยงกับ

- Appointment
- Patient
- Doctor

มี Unique Constraint ที่ appointment_id

## 6. คำศัพท์

**Primary Key:** ค่าที่ใช้ระบุข้อมูลแต่ละรายการ

**Foreign Key:** ค่าที่ใช้เชื่อมข้อมูลระหว่างตาราง

**ORM:** วิธีจัดการ Database ผ่าน Object/Model ในโปรแกรมแทนการเขียน SQL ทุกกรณีโดยตรง

**Migration:** การจัดการการเปลี่ยนแปลงโครงสร้าง Database
