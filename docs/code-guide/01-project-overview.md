# Code Guide 01: ภาพรวมโปรเจกต์

## 1. โครงสร้างหลัก

```text
hospital-appointment-system/
├── backend/
├── mobile/
├── web/
└── docs/
```

## 2. Backend

Backend อยู่ใน `backend/` และมีโครงสร้าง

```text
backend/app/
├── core/
├── models/
├── repositories/
├── routers/
├── schemas/
├── services/
├── utils/
└── main.py
```

## 3. Mobile

```text
mobile/lib/
├── core/
├── features/
└── main.dart
```

## 4. Web

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

## 5. ภาพรวมการทำงาน

```text
Mobile ──┐
         ├──> FastAPI Backend ──> PostgreSQL
Web ─────┘
```

Backend เป็นตัวกลางระหว่าง Client และ Database
