# Code Guide 08: Medical Record

## 1. Medical Record คืออะไร

Medical Record ใช้เก็บข้อมูลที่เกี่ยวข้องกับการรักษา

ข้อมูลหลัก ได้แก่

- Chief Complaint
- Present Illness
- Physical Examination
- Diagnosis
- Treatment
- Recommendation
- Note

## 2. ความสัมพันธ์

```text
Appointment
     │
     ▼
Medical Record
     ├── Patient
     └── Doctor
```

Appointment หนึ่งรายการมี Medical Record ได้หนึ่งรายการ โดย Backend กำหนด Unique Constraint ที่ appointment_id

## 3. API

```text
POST  /medical-records
GET   /medical-records
GET   /medical-records/doctor/history
GET   /medical-records/{medical_record_id}
PATCH /medical-records/{medical_record_id}
```

## 4. สิทธิ์

การอ่าน Medical Record ตรวจสอบ Role ของ Current User

- Doctor เข้าถึงข้อมูลที่เกี่ยวข้องกับ Doctor
- Patient เข้าถึงข้อมูลของตนเอง
- Role อื่นถูกปฏิเสธสำหรับ Endpoint รายการ Medical Record

## 5. คำถามที่ควรตอบได้

**Q: ทำไม Medical Record ต้องผูกกับ Appointment?**

A: เพื่อระบุว่าเวชระเบียนนั้นเกิดจากการนัดหมายรายการใด

**Q: ทำไม appointment_id ต้องไม่ซ้ำ?**

A: เพื่อให้ Appointment หนึ่งรายการมี Medical Record ได้หนึ่งรายการตามโครงสร้างที่กำหนดใน Model
