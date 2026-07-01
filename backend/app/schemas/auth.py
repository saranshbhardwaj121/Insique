from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    identifier: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=128)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthTokensResponse(TokenResponse):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=10)
    password: str = Field(min_length=8, max_length=128)


class PasswordResetResponse(BaseModel):
    message: str


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)
