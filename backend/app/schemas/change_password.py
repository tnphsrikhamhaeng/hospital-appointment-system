from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.core.validators import validate_password_strength


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(
        min_length=8,
        max_length=20,
    )

    new_password: str = Field(
        min_length=8,
        max_length=20,
    )

    confirm_password: str = Field(
        min_length=8,
        max_length=20,
    )

    @model_validator(mode="after")
    def validate_passwords(self) -> "ChangePasswordRequest":
        validate_password_strength(self.new_password)

        if self.new_password != self.confirm_password:
            raise ValueError("Password mismatch")

        return self

    model_config = ConfigDict(
        extra="forbid",
    )