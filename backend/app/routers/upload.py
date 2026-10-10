
from __future__ import annotations

import os
import uuid
from io import BytesIO

import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, File, HTTPException, UploadFile, status


router = APIRouter(
    prefix="/uploads",
    tags=["Uploads"],
)

ALLOWED_CONTENT_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MAX_FILE_SIZE = 5 * 1024 * 1024


async def _upload_image(
    file: UploadFile,
    folder: str,
) -> str:
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        await file.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="รองรับเฉพาะไฟล์ JPG, PNG และ WEBP",
        )

    try:
        contents = await file.read(MAX_FILE_SIZE + 1)
    finally:
        await file.close()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ขนาดรูปภาพต้องไม่เกิน 5 MB",
        )

    cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
    api_key = os.getenv("CLOUDINARY_API_KEY")
    api_secret = os.getenv("CLOUDINARY_API_SECRET")

    if not all([cloud_name, api_key, api_secret]):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cloudinary configuration is missing",
        )

    try:
        result = cloudinary.uploader.upload(
            BytesIO(contents),
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            folder=folder,
            public_id=str(uuid.uuid4()),
            resource_type="image",
            overwrite=False,
        )

        return result["secure_url"]

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="ไม่สามารถอัปโหลดรูปภาพได้",
        )


@router.post(
    "/department-image",
    status_code=status.HTTP_201_CREATED,
)
async def upload_department_image(
    file: UploadFile = File(...),
):
    image_url = await _upload_image(
        file=file,
        folder="careflow/departments",
    )

    return {
        "image_url": image_url,
    }


@router.post(
    "/doctor-image",
    status_code=status.HTTP_201_CREATED,
)
async def upload_doctor_image(
    file: UploadFile = File(...),
):
    image_url = await _upload_image(
        file=file,
        folder="careflow/doctors",
    )

    return {
        "image_url": image_url,
    }
