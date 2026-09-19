from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status


router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)


DEPARTMENT_UPLOAD_DIR = (
    Path(__file__).resolve().parent.parent
    / "uploads"
    / "departments"
)

DOCTOR_UPLOAD_DIR = (
    Path(__file__).resolve().parent.parent
    / "uploads"
    / "doctors"
)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024


async def _save_image(
    file: UploadFile,
    upload_dir: Path,
) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="รองรับเฉพาะไฟล์ JPG, PNG และ WEBP",
        )

    extension = ALLOWED_CONTENT_TYPES[file.content_type]

    upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = f"{uuid.uuid4()}{extension}"
    file_path = upload_dir / filename

    total_size = 0

    try:
        with file_path.open("wb") as output_file:
            while chunk := await file.read(1024 * 1024):
                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    file_path.unlink(missing_ok=True)

                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="ขนาดรูปภาพต้องไม่เกิน 5 MB",
                    )

                output_file.write(chunk)

    finally:
        await file.close()

    return filename


@router.post(
    "/department-image",
    status_code=status.HTTP_201_CREATED,
)
async def upload_department_image(
    request: Request,
    file: UploadFile = File(...),
):
    filename = await _save_image(
        file=file,
        upload_dir=DEPARTMENT_UPLOAD_DIR,
    )

    image_url = (
        f"{request.base_url}uploads/departments/{filename}"
    )

    return {
        "image_url": image_url,
    }


@router.post(
    "/doctor-image",
    status_code=status.HTTP_201_CREATED,
)
async def upload_doctor_image(
    request: Request,
    file: UploadFile = File(...),
):
    filename = await _save_image(
        file=file,
        upload_dir=DOCTOR_UPLOAD_DIR,
    )

    image_url = (
        f"{request.base_url}uploads/doctors/{filename}"
    )

    return {
        "image_url": image_url,
    }