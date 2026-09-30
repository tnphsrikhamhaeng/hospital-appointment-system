# Code Guide 09: Notification

## 1. Notification คืออะไร

Notification เป็นส่วนของระบบสำหรับจัดการข้อมูลการแจ้งเตือน และมี Notification Settings สำหรับการตั้งค่าที่เกี่ยวข้อง

## 2. Backend

Backend มี Router สำหรับ

- notification
- notification_setting

และมี Scheduler ใน core

## 3. Scheduler Flow

```text
Backend Start
 ↓
start_scheduler()
 ↓
Scheduled Jobs
 ↓
Notification Processing
 ↓
Backend Stop
 ↓
stop_scheduler()
```

## 4. Mobile

Mobile Project มี Package ที่เกี่ยวข้องกับ Notification ได้แก่

- onesignal_flutter
- firebase_messaging
- flutter_local_notifications

รายละเอียดการใช้งานจริงควรอ่านจาก Source Code ของ Version ปัจจุบัน

## 5. คำถามที่ควรตอบได้

**Q: Scheduler คืออะไร?**

A: ส่วนที่ใช้เรียกงานตามเวลาหรือกำหนดการที่ระบบตั้งไว้

**Q: Scheduler เริ่มทำงานเมื่อใด?**

A: Backend เริ่ม Scheduler ในช่วง Application lifespan
