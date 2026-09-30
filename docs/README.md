# CareFlow

ระบบจองคิวการพบแพทย์และติดตามการนัดหมายผ่าน Mobile Application
ร่วมกับ Web Application สำหรับบุคลากรโรงพยาบาลและแพทย์

---

## Project Overview

CareFlow เป็นระบบสำหรับจัดการกระบวนการนัดหมายผู้ป่วยและการเข้ารับบริการทางการแพทย์
โดยระบบแบ่งการใช้งานออกเป็น 2 ส่วนหลัก ได้แก่

- Mobile Application สำหรับผู้ป่วย
- Web Application สำหรับแพทย์และบุคลากรโรงพยาบาล

ทั้งสองส่วนเชื่อมต่อกับ Backend API เดียวกันผ่าน REST API
และใช้ PostgreSQL เป็นฐานข้อมูลกลาง

ระบบประกอบด้วยส่วนหลักดังนี้

```text
Mobile Application
       │
       │ REST API
       ▼
   FastAPI Backend
       │
       │ SQLAlchemy
       ▼
 PostgreSQL Database

Web Application
       │
       │ REST API
       ▼
   FastAPI Backend