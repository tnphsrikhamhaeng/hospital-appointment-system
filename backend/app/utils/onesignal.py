from __future__ import annotations

import logging
import time
from typing import Any

import httpx

from app.core.config import settings


logger = logging.getLogger(__name__)

ONESIGNAL_API_URL = "https://api.onesignal.com/notifications"


def send_notification(
    *,
    external_id: str,
    title: str,
    body: str,
) -> dict[str, Any]:

    payload = {
        "app_id": settings.ONESIGNAL_APP_ID,
        "target_channel": "push",
        "include_aliases": {
            "external_id": [
                external_id,
            ],
        },
        "headings": {
            "en": title,
            "th": title,
        },
        "contents": {
            "en": body,
            "th": body,
        },
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Key {settings.ONESIGNAL_API_KEY}",
    }

    start_time = time.perf_counter()

    response = httpx.post(
        ONESIGNAL_API_URL,
        headers=headers,
        json=payload,
        timeout=10.0,
    )

    elapsed = time.perf_counter() - start_time

    logger.info(
        "OneSignal API request completed. "
        "elapsed=%.3fs status=%s",
        elapsed,
        response.status_code,
    )

    if response.is_error:
        logger.error(
            "OneSignal API error. "
            "status=%s response=%s",
            response.status_code,
            response.text,
        )

    response.raise_for_status()

    return response.json()