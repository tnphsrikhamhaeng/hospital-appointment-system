from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.user_device import UserDevice
from app.repositories.user_device_repository import (
    UserDeviceRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.user_device_schema import (
    UserDeviceRegisterRequest,
    UserDeviceResponse,
)

class UserDeviceService:

    def __init__(
        self,
        db: Session,
    ):
        self.db = db

        self.user_repository = UserRepository(db)
        self.user_device_repository = (
            UserDeviceRepository(db)
        )
        
    def register_or_update_device(
        self,
        user_id,
        request: UserDeviceRegisterRequest,
    ) -> UserDeviceResponse:
      
        user = self.user_repository.get_by_id(
            user_id,
        )

        if user is None:
            raise NotFoundException(
                detail="User not found.",
            )

        user_device = (
            self.user_device_repository.get_by_device_token(
                request.device_token,
            )
        )

        if user_device is None:
            user_device = self._create_device(
                user_id=user.id,
                request=request,
            )
        else:
            user_device = self._update_device(
                user_device=user_device,
                request=request,
            )

        self.db.commit()
        self.db.refresh(user_device)

        return UserDeviceResponse.model_validate(
            user_device,
        )
        
    def get_active_devices(
        self,
        user_id,
    ) -> list[UserDevice]:
        return (
            self.user_device_repository
            .get_active_devices_by_user_id(
                user_id,
            )
        )
        
    def deactivate_device(
        self,
        device_id,
    ) -> None:
        user_device = (
            self.user_device_repository.get_by_id(
                device_id,
            )
        )

        if user_device is None:
            raise NotFoundException(
                detail="Device not found.",
            )
        
        user_device.is_active = False
        user_device.last_used_at = (
              datetime.now(timezone.utc)
          )

        self.user_device_repository.update(
              user_device,
          )

        self.db.commit()
        
        
    def _create_device(
        self,
        *,
        user_id,
        request: UserDeviceRegisterRequest,
    ) -> UserDevice:
          user_device = UserDevice(
            user_id=user_id,
            device_token=request.device_token,
            platform=request.platform,
            device_name=request.device_name,
        )

          return self.user_device_repository.create(
              user_device,
          )
    
    def _update_device(
        self,
        *,
        user_device: UserDevice,
        request: UserDeviceRegisterRequest,
    ) -> UserDevice:
      
        user_device.platform = request.platform
        user_device.device_name = request.device_name
        user_device.is_active = True
        user_device.last_used_at = (
            datetime.now(timezone.utc)
        )

        return self.user_device_repository.update(
            user_device,
        )