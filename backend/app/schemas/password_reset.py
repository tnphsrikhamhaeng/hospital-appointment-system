from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.core.validators import validate_password_strength


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    model_config = ConfigDict(
        extra="forbid",
    )


class ResetPasswordRequest(BaseModel):
    reset_token: str = Field(
        min_length=1,
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
    def validate_passwords(self) -> "ResetPasswordRequest":
        validate_password_strength(
            self.new_password,
        )

        if self.new_password != self.confirm_password:
            raise ValueError("Password mismatch")

        return self

    model_config = ConfigDict(
        extra="forbid",
    )
    
class StaffForgotPasswordRequest(BaseModel):
    username: str = Field(
        min_length=1,
        max_length=50,
    )

    model_config = ConfigDict(
        extra="forbid",
    )