# Notification Documentation

## 1. Overview
ระบบมีส่วนจัดการ Notification และ Notification Settings

## 2. Backend Components
Backend มี Router แยกสำหรับ Notification และ Notification Setting และมี Scheduler ใน app/core/scheduler

## 3. Scheduler
~~~text
Application Startup
       │
       ▼
start_scheduler()
       │
       ▼
Scheduled Jobs
       │
       ▼
Notification Processing
       │
       ▼
Application Shutdown
       │
       ▼
stop_scheduler()
~~~

## 4. Notification API
Notification เป็นหนึ่งในกลุ่ม Router ที่ถูก Register ใน Backend สำหรับจัดการข้อมูล Notification

## 5. Notification Settings
ระบบมี Router สำหรับ Notification Settings

## 6. Mobile Notification Support
Mobile Project มี Package ได้แก่ onesignal_flutter, firebase_messaging และ flutter_local_notifications ตาม pubspec.yaml

## 7. หมายเหตุ
Scheduler เป็นส่วนหนึ่งของ Backend Process ดังนั้น Scheduled Notification ขึ้นอยู่กับสถานะการทำงานของ Backend Service
