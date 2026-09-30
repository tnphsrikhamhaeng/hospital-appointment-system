# CareFlow Hospital Appointment System

CareFlow เป็นระบบจองคิวการพบแพทย์และติดตามการนัดหมาย ประกอบด้วย Mobile Application, Web Application, Backend API และ PostgreSQL Database

## Components
- Mobile Application: Flutter / Dart
- Web Application: React / TypeScript / Vite
- Backend API: Python / FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Database Migration: Alembic

## User Roles
- PATIENT
- DOCTOR
- HOSPITAL_STAFF

## Main Functions
- Authentication และการจัดการบัญชีผู้ใช้
- การจัดการข้อมูลแพทย์ แผนก และความเชี่ยวชาญ
- การจองและจัดการ Appointment
- การจัดการตารางแพทย์
- Appointment QR Code
- Medical Record
- Notification และ Notification Settings
- Profile และ Change Password
- Password Reset
- File Upload

## Project Structure
~~~text
hospital-appointment-system/
├── backend/
├── mobile/
├── web/
└── docs/
~~~

## Documentation
- [Architecture](docs/architecture.md)
- [Backend](docs/backend.md)
- [Mobile](docs/mobile.md)
- [Web](docs/web.md)
- [Database](docs/database.md)
- [API](docs/api.md)
- [Notification](docs/notification.md)
- [Deployment](docs/deployment.md)

## Backend Development
~~~bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
~~~

API Documentation ของ FastAPI สามารถดูได้ที่ /docs

## Web Development
~~~bash
cd web
npm install
npm run dev
~~~

Build Production:
~~~bash
npm run build
~~~

## Mobile Development
~~~bash
cd mobile
flutter pub get
flutter run
~~~

สร้าง Android APK สำหรับ Production:
~~~bash
flutter build apk --release --dart-define=API_BASE_URL=https://<backend-url>
~~~

## Repository
https://github.com/tnphsrikhamhaeng/hospital-appointment-system
