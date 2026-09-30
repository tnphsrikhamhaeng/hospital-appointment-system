# Code Guide 02: Backend

## 1. Backend คืออะไร

Backend คือส่วนที่รับ Request จาก Mobile และ Web แล้วประมวลผลข้อมูลและติดต่อ Database

Backend ของ CareFlow ใช้ FastAPI

## 2. ส่วนสำคัญ

```text
core/
models/
repositories/
routers/
schemas/
services/
utils/
```

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

```text
Client
 ↓
Router
 ↓
Service
 ↓
Repository
 ↓
Database
```

## 4. คำถามที่ควรตอบได้

**Q: FastAPI ทำหน้าที่อะไร?**

A: เป็น Framework ที่ใช้สร้าง Backend API ของระบบ

**Q: Router กับ Service ต่างกันอย่างไร?**

A: Router รับ Request และเรียก Service ส่วน Service ทำหน้าที่ประมวลผล Logic ของระบบ

**Q: ทำไมต้องแยกส่วน?**

A: เพื่อให้แต่ละส่วนมีหน้าที่ชัดเจนและจัดการโค้ดได้ง่ายขึ้น
