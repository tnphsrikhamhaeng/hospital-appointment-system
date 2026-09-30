# Code Guide 07: Appointment

## 1. Appointment คืออะไร

เป็นข้อมูลหลักสำหรับการนัดหมายระหว่างผู้ป่วยกับแพทย์

## 2. Flow การสร้าง Appointment

```text
ผู้ป่วย
 ↓
Mobile
 ↓
POST /appointments
 ↓
Appointment Router
 ↓
AppointmentService
 ↓
Database
 ↓
Appointment Response
 ↓
Mobile
```

## 3. Endpoint สำคัญ

```text
POST   /appointments
GET    /appointments/search
GET    /appointments/my
GET    /appointments/my/schedule
GET    /appointments/{appointment_id}
PATCH  /appointments/{appointment_id}/reschedule
PATCH  /appointments/{appointment_id}/cancel
PATCH  /appointments/{appointment_id}/status
```

## 4. ความสัมพันธ์

Appointment มี patient_id, doctor_id และ department_id เป็นข้อมูลสำหรับเชื่อมกับ Entity ที่เกี่ยวข้อง

Appointment ยังมีความสัมพันธ์กับ QR Code และ Medical Record

## 5. การเปลี่ยนสถานะ

การเปลี่ยนสถานะใช้ Endpoint

```text
PATCH /appointments/{appointment_id}/status
```

Backend ตรวจสอบ Role ของ Current User ก่อนดำเนินการ

## 6. คำถามที่ควรตอบได้

**Q: ทำไม Appointment ต้องมี doctor_id?**

A: เพื่อระบุว่า Appointment นั้นนัดกับแพทย์คนใด

**Q: ทำไมต้องมี department_id?**

A: เพื่อระบุแผนกที่เกี่ยวข้องกับ Appointment
