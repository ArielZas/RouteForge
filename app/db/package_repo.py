from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import Package, PackageUpdate
from app.db.models import PackageModel


def create_package(db: Session, package: Package) -> PackageModel:
    db_package = PackageModel(**package.model_dump())
    db.add(db_package)
    db.commit()
    db.refresh(db_package)
    return db_package


def list_packages(db: Session) -> list[PackageModel]:
    return db.query(PackageModel).order_by(PackageModel.id).all()


def get_package(db: Session, package_id: int) -> PackageModel | None:
    return db.get(PackageModel, package_id)


def update_package(
    db: Session,
    db_package: PackageModel,
    package: PackageUpdate,
) -> PackageModel:
    changes = package.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(db_package, field, value)

    db.commit()
    db.refresh(db_package)
    return db_package


def delete_package(db: Session, db_package: PackageModel) -> None:
    db.delete(db_package)
    db.commit()
