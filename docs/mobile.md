# Mobile Application Documentation

## 1. Technology
Mobile Application พัฒนาด้วย Flutter และ Dart

Dependencies สำคัญใน pubspec.yaml ได้แก่ dio, flutter_secure_storage, qr_flutter, firebase_core, firebase_messaging, flutter_local_notifications และ onesignal_flutter

## 2. Structure
~~~text
mobile/lib/
├── core/
├── features/
└── main.dart
~~~

Assets ที่กำหนด ได้แก่ Department images, Logo images และ Kanit fonts

## 3. Backend Connection
Mobile ใช้ค่า API_BASE_URL จาก Dart Environment

~~~bash
flutter run --dart-define=API_BASE_URL=https://<backend-url>
~~~

หากไม่กำหนดค่า จะใช้ค่า Default ที่กำหนดไว้ใน Source Code

## 4. HTTP Communication
Mobile ใช้ Dio สำหรับติดต่อ Backend API

## 5. Secure Storage
Project มี flutter_secure_storage สำหรับข้อมูลที่ต้องการจัดเก็บอย่างปลอดภัยบนอุปกรณ์

## 6. QR Code
Project มี qr_flutter สำหรับการทำงานเกี่ยวกับ QR Code

## 7. Notification
Mobile มี Package สำหรับ Push และ Local Notification ตามที่ระบุใน pubspec.yaml

## 8. Build APK
~~~bash
flutter clean
flutter pub get
flutter build apk --release --dart-define=API_BASE_URL=https://<backend-url>
~~~

ไฟล์ APK จะอยู่ภายใต้ build/app/outputs/flutter-apk/
