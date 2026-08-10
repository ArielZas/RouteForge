from datetime import time

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import Float, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.api.schemas import PackageStatus
from app.db.database import Base


class PackageModel(Base):
    __tablename__ = "packages"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        index=True
    )
    source_address: Mapped[str] = mapped_column(String(255))
    source_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    destination_address: Mapped[str] = mapped_column(String(255))
    destination_latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    destination_longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    deadline: Mapped[time] = mapped_column(Time)
    status: Mapped[PackageStatus] = mapped_column(
        SqlEnum(PackageStatus, native_enum=False),
        default=PackageStatus.WAITING,
    )
