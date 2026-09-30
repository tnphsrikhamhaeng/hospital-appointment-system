# Code Guide 04: Web

## 1. Web ใช้อะไร

Web พัฒนาด้วย React และ TypeScript และใช้ Vite

Package สำคัญจาก package.json ได้แก่

- axios
- react-router-dom
- lucide-react

## 2. โครงสร้าง

```text
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
```

## 3. API

Web ใช้ Axios ติดต่อ Backend

```text
React
 ↓
Axios
 ↓
FastAPI
```

## 4. Routing

ใช้ react-router-dom สำหรับจัดการเส้นทางของหน้า Web

## 5. คำถามที่ควรตอบได้

**Q: React ทำหน้าที่อะไร?**

A: ใช้สร้างส่วนติดต่อผู้ใช้ของ Web Application

**Q: Axios ใช้ทำอะไร?**

A: ใช้ติดต่อ Backend API

**Q: React Router ใช้ทำอะไร?**

A: ใช้จัดการเส้นทางและหน้าใน Web Application
