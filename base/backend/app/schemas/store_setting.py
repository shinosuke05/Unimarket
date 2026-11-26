from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class StoreSettingUpdate(BaseModel):
    qr_image_url: str | None = Field(default=None, max_length=500)
    bank_name: str | None = Field(default=None, max_length=100)
    bank_account_number: str | None = Field(default=None, max_length=50)
    bank_account_holder: str | None = Field(default=None, max_length=100)
    phone: str | None = Field(default=None, max_length=20)
    zalo: str | None = Field(default=None, max_length=100)
    facebook_url: str | None = Field(default=None, max_length=255)


class StoreSettingOut(StoreSettingUpdate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    updated_at: datetime