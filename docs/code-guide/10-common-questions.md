# Code Guide 10: คำถามที่อาจารย์ถามบ่อย

## Architecture

### Q: ระบบแบ่งเป็นส่วนอะไรบ้าง?
A: Mobile Application, Web Application, Backend API และ PostgreSQL Database

### Q: Backend อยู่ตรงไหน?
A: อยู่ในโฟลเดอร์ backend และใช้ FastAPI

### Q: Mobile กับ Database ติดต่อกันโดยตรงหรือไม่?
A: Mobile ติดต่อ Backend API ก่อน และ Backend เป็นส่วนที่ติดต่อ Database

## Backend

### Q: Router คืออะไร?
A: ส่วนที่รับ API Request และส่งต่อการทำงานไปยังส่วนที่เกี่ยวข้อง

### Q: Service คืออะไร?
A: ส่วนที่ประมวลผล Business Logic

### Q: Repository คืออะไร?
A: ส่วนที่จัดการการเข้าถึงข้อมูล

### Q: Schema คืออะไร?
A: โครงสร้างข้อมูลสำหรับตรวจสอบและกำหนดรูปแบบ Request/Response

### Q: Model คืออะไร?
A: โครงสร้างที่ใช้แทนข้อมูลใน Database ผ่าน ORM

## Database

### Q: PostgreSQL ใช้ทำอะไร?
A: ใช้เป็น Database หลักของระบบ

### Q: SQLAlchemy ใช้ทำอะไร?
A: ใช้เป็น ORM สำหรับติดต่อและจัดการข้อมูลใน Database

### Q: Alembic ใช้ทำอะไร?
A: ใช้จัดการ Database Migration

## Mobile

### Q: Flutter ใช้ทำอะไร?
A: ใช้พัฒนา Mobile Application

### Q: Dio ใช้ทำอะไร?
A: ใช้ติดต่อ Backend API

## Web

### Q: React ใช้ทำอะไร?
A: ใช้พัฒนา Web User Interface

### Q: Axios ใช้ทำอะไร?
A: ใช้ติดต่อ Backend API

## Appointment

### Q: Appointment เชื่อมกับอะไร?
A: Patient, Doctor, Department, QR Code และ Medical Record

### Q: ใครเปลี่ยน Appointment Status ได้?
A: Backend ตรวจสอบให้ Doctor หรือ Hospital Staff เป็นผู้ดำเนินการ Endpoint นี้

## Medical Record

### Q: ใครเข้าถึง Medical Record ได้?
A: Backend ตรวจสอบสิทธิ์ โดย Patient เข้าถึงข้อมูลของตนเอง และ Doctor เข้าถึงข้อมูลตาม Doctor ID ที่เกี่ยวข้อง

## วิธีตอบเมื่อไม่แน่ใจ

ไม่ควรเดาโค้ดที่ไม่ได้อ่าน ให้ตอบตาม Source Code ของ Version ที่ใช้งานจริง และเปิดไฟล์ที่เกี่ยวข้องเพื่ออธิบาย Flow ประกอบ
