from pydantic import BaseModel, EmailStr
from typing import Optional

class SignupRequest(BaseModel):
    name:     str
    email:    str
    password: str
    age:      int
    gender:   str  


class LoginRequest(BaseModel):
    email:    str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user: dict

class ReportSummary(BaseModel):
    report_id:        int
    uploaded_at:      str
    health_score:     Optional[int]
    biomarkers_found: int

    class Config:
        from_attributes = True