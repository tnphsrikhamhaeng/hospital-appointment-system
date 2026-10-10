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

          FastAPI API ──HTTPS──► Cloudinary
                                  Image Storage
~~~

## 7. Environment Configuration
Backend อ่าน Configuration ผ่าน Settings และ Environment Variables

Mobile สามารถกำหนด Backend URL ผ่าน API_BASE_URL

### Cloudinary Image Storage
Backend ใช้ Cloudinary เก็บรูปภาพที่อัปโหลดผ่าน API แทนการเก็บไฟล์ไว้ใน Local Filesystem ของ Render

กำหนด Environment Variables ต่อไปนี้ใน Render Dashboard ของ **Backend Service**:
- `CLOUDINARY_CLOUD_NAME`
- `CLOUDINARY_API_KEY`
- `CLOUDINARY_API_SECRET`

ขั้นตอนตั้งค่า:
1. เปิด Render Dashboard และเลือก Backend Service
2. ไปที่ Environment แล้วเพิ่มตัวแปรทั้งสาม โดยใช้ค่าจาก Cloudinary Console
3. บันทึกการเปลี่ยนแปลงและรอให้ Backend Deploy จนสถานะเป็น Live
4. เปิด `/docs` ของ Backend แล้วทดสอบ `POST /uploads/department-image` หรือ `POST /uploads/doctor-image`
5. ตรวจว่า Response ได้สถานะ `201` และ `image_url` เป็น Secure URL ของ Cloudinary

ห้ามใส่ API Secret ใน Source Code, Frontend, GitHub Repository หรือเอกสาร ห้ามเปิดเผยค่าของ Secret ในภาพหน้าจอหรือข้อความสาธารณะ

### Upload API
~~~text
POST /uploads/department-image
POST /uploads/doctor-image
~~~

ทั้งสอง Endpoint รับไฟล์ผ่าน `multipart/form-data` ชื่อ field `file` รองรับ JPEG, PNG และ WEBP ขนาดไม่เกิน 5 MB

URL จาก Cloudinary จะถูกส่งกลับใน `image_url` เพื่อให้ระบบนำไปบันทึกกับข้อมูลแผนกหรือแพทย์ การเพิ่มรูปใหม่ผ่านระบบจึงไม่ต้องเพิ่มไฟล์ลงใน Web project หรือ Deploy Web ใหม่ทุกครั้ง

## 8. Deployment Checklist
- Database URL
- Backend Environment Variables
- Cloudinary Environment Variables
- CORS Origins
- Backend API URL
- Web Build
- Mobile API URL
- Database Migration
- Authentication
- Notification Scheduler
- ทดสอบอัปโหลดรูปแผนกและรูปแพทย์บน Production
