# Deployment Documentation

## 1. Overview
ระบบแบ่ง Deployment ออกเป็น Backend API, Web Application, Database และ Mobile Application

## 2. Backend
~~~bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
~~~

Backend ต้องมี Configuration และ Database URL ที่จำเป็นก่อนเริ่มทำงาน

## 3. Web
~~~bash
npm install
npm run build
~~~

ผลลัพธ์อยู่ใน web/dist/

## 4. Mobile
~~~bash
flutter build apk --release --dart-define=API_BASE_URL=https://<backend-url>
~~~

## 5. Database
Database ใช้ PostgreSQL และจัดการ Schema ด้วย Alembic

## 6. Production Architecture
~~~text
Mobile APK ──────┐
                 │ HTTPS
                 ▼
          ┌───────────────┐
Web App ─►│ FastAPI API   │
          └───────┬───────┘
                  │
                  ▼
             PostgreSQL
~~~

## 7. Environment Configuration
Backend อ่าน Configuration ผ่าน Settings และ Environment Variables

Mobile สามารถกำหนด Backend URL ผ่าน API_BASE_URL

## 8. Deployment Checklist
- Database URL
- Backend Environment Variables
- CORS Origins
- Backend API URL
- Web Build
- Mobile API URL
- Database Migration
- Authentication
- Notification Scheduler
