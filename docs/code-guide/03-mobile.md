# Code Guide 03: Mobile

## 1. Mobile ใช้อะไร

Mobile พัฒนาด้วย Flutter และ Dart

โครงสร้างหลัก

```text
mobile/lib/
├── core/
├── features/
└── main.dart
```

## 2. การติดต่อ Backend

Mobile ใช้ Dio ติดต่อ API

```text
Flutter
 ↓
Dio
 ↓
FastAPI
```

Backend URL สามารถกำหนดผ่าน

```text
API_BASE_URL
```

ตัวอย่าง

```bash
flutter run --dart-define=API_BASE_URL=https://<backend-url>
```

## 3. สิ่งที่ควรเข้าใจ

เมื่อผู้ใช้กดปุ่ม เช่น จองนัดหมาย Application จะสร้าง Request แล้วส่งไป Backend จากนั้นนำ Response มาใช้แสดงผล

## 4. Package สำคัญ

จาก pubspec.yaml มี Package เช่น

- dio
- flutter_secure_storage
- qr_flutter
- firebase_core
- firebase_messaging
- flutter_local_notifications
- onesignal_flutter

## 5. คำถามที่ควรตอบได้

**Q: Flutter ทำหน้าที่อะไร?**

A: ใช้สร้าง Mobile Application

**Q: Dio ใช้ทำอะไร?**

A: ใช้ส่ง HTTP Request และรับ Response จาก Backend API

**Q: API_BASE_URL คืออะไร?**

A: URL ของ Backend ที่ Mobile ใช้ติดต่อ API
