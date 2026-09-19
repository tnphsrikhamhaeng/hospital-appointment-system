from __future__ import annotations

import firebase_admin
from firebase_admin import credentials, messaging

from app.core.config import settings


_firebase_app: firebase_admin.App | None = None


def _get_firebase_app() -> firebase_admin.App:
    global _firebase_app

    if _firebase_app is not None:
        return _firebase_app

    if not firebase_admin._apps:
        cred = credentials.Certificate(
            settings.FIREBASE_CREDENTIALS_PATH,
        )

        _firebase_app = firebase_admin.initialize_app(
            cred,
        )
    else:
        _firebase_app = firebase_admin.get_app()

    return _firebase_app


def send_notification(
    *,
    device_token: str,
    title: str,
    body: str,
) -> str:
    _get_firebase_app()

    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token=device_token,
    )

    return messaging.send(message)