from datetime import time
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PackageStatus(str, Enum):
    WAITING = "waiting"
    PICKED_UP = "picked_up"
    DELIVERED = "delivered"


class Package(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    source_address: str = Field(min_length=1, max_length=255)
    source_latitude: float | None = Field(default=None, ge=-90, le=90)
    source_longitude: float | None = Field(default=None, ge=-180, le=180)

    destination_address: str = Field(min_length=1, max_length=255)
    destination_latitude: float | None = Field(default=None, ge=-90, le=90)
    destination_longitude: float | None = Field(default=None, ge=-180, le=180)

    deadline: time = Field(ge=time(8, 0), le=time(23, 59))


class PackageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0)
    source_address: str = Field(min_length=1, max_length=255)
    source_latitude: float | None = Field(default=None, ge=-90, le=90)
    source_longitude: float | None = Field(default=None, ge=-180, le=180)

    destination_address: str = Field(min_length=1, max_length=255)
    destination_latitude: float | None = Field(default=None, ge=-90, le=90)
    destination_longitude: float | None = Field(default=None, ge=-180, le=180)

    deadline: time = Field(ge=time(8, 0), le=time(23, 59))

    status: PackageStatus


class PackageUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    source_address: str | None = Field(default=None, min_length=1, max_length=255)
    source_latitude: float | None = Field(default=None, ge=-90, le=90)
    source_longitude: float | None = Field(default=None, ge=-180, le=180)
    destination_address: str | None = Field(
        default=None, min_length=1, max_length=255
    )
    destination_latitude: float | None = Field(default=None, ge=-90, le=90)
    destination_longitude: float | None = Field(default=None, ge=-180, le=180)
    deadline: time | None = Field(default=None, ge=time(8, 0), le=time(23, 59))
    status: PackageStatus | None = None
