from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Response, status
from sqlalchemy.orm import Session

from app.api.schemas import Package, PackageResponse, PackageUpdate
from app.db import package_repo
from app.db.database import get_db


router = APIRouter(prefix="/packages", tags=["packages"])
PackageId = Annotated[int, Path(gt=0)]


@router.post("", response_model=PackageResponse, status_code=status.HTTP_201_CREATED)
def create_package(package: Package, db: Session = Depends(get_db)) -> PackageResponse:
    db_package = package_repo.create_package(db, package)
    return PackageResponse.model_validate(db_package)


@router.get("", response_model=list[PackageResponse])
def list_packages(db: Session = Depends(get_db)) -> list[PackageResponse]:
    db_packages = package_repo.list_packages(db)
    return [PackageResponse.model_validate(package) for package in db_packages]


@router.get("/{package_id}", response_model=PackageResponse)
def get_package(package_id: PackageId, db: Session = Depends(get_db)) -> PackageResponse:
    db_package = package_repo.get_package(db, package_id)
    if db_package is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    return PackageResponse.model_validate(db_package)


@router.patch("/{package_id}", response_model=PackageResponse)
def update_package(
    package_id: PackageId,
    package: PackageUpdate,
    db: Session = Depends(get_db),
) -> PackageResponse:
    db_package = package_repo.get_package(db, package_id)
    if db_package is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    updated_package = package_repo.update_package(db, db_package, package)
    return PackageResponse.model_validate(updated_package)


@router.delete("/{package_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_package(package_id: PackageId, db: Session = Depends(get_db)) -> Response:
    db_package = package_repo.get_package(db, package_id)
    if db_package is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Package not found")
    package_repo.delete_package(db, db_package)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
