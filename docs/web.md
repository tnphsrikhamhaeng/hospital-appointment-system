# Web Application Documentation

## 1. Technology
Web Application ใช้ React, TypeScript, Vite, React Router, Axios และ Lucide React

## 2. Structure
~~~text
web/src/
├── api/
├── assets/
├── features/
├── hooks/
├── utils/
├── App.tsx
├── App.css
├── index.css
└── main.tsx
~~~

## 3. API Communication
Web ใช้ Axios ติดต่อ Backend API

## 4. Routing
ระบบใช้ react-router-dom สำหรับจัดการ Routing ของ Web Application

หน้าและ Layout ถูกแบ่งตามส่วนการใช้งานของระบบ เช่น Staff และ Doctor

## 5. Build
~~~bash
npm install
npm run dev
npm run build
~~~

คำสั่ง Build จะตรวจสอบ TypeScript ก่อนสร้างไฟล์สำหรับ Production

## 6. Lint
~~~bash
npm run lint
~~~

## 7. Deployment
Web Application ถูก Build เป็น Static Files ภายใน Directory dist และสามารถนำไป Deploy ผ่าน Static Web Hosting
