# Database Documentation

## 1. Database Technology
ระบบใช้ PostgreSQL และ SQLAlchemy ORM สำหรับการติดต่อ Database โดยใช้ Alembic สำหรับ Database Migration

## 2. Database Connection
~~~text
FastAPI
   │
   ▼
SQLAlchemy
   │
   ▼
PostgreSQL
~~~

## 3. User
ตาราง users เก็บข้อมูล เช่น id, username, email, password, first_name, last_name, phone_number, gender, date_of_birth, role, status, created_at และ updated_at

Role หลักคือ PATIENT, DOCTOR และ HOSPITAL_STAFF

## 4. Appointment
ตาราง appointments เชื่อมโยงกับ users, doctors และ departments

ข้อมูลสำคัญ ได้แก่ appointment_date, start_time, end_time, reason, status, cancelled_reason, cancelled_at, confirmed_at, created_at และ updated_at

## 5. Medical Record
ตาราง medical_records เชื่อมโยงกับ appointments, users และ doctors

ข้อมูลประกอบด้วย chief_complaint, present_illness, physical_examination, diagnosis, treatment, recommendation และ note

Appointment หนึ่งรายการมี Medical Record ได้หนึ่งรายการ โดยมี Unique Constraint ที่ appointment_id

## 6. Index
Medical Record มี Index สำหรับ patient_id, doctor_id และ created_at

## 7. Migration
การเปลี่ยนแปลง Schema ของ Database จัดการผ่าน Alembic Migration
