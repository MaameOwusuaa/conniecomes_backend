from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_admin_user
from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceUpdate


router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=list[ServiceResponse])
def list_services(db: Session = Depends(get_db)):
    return (
        db.query(Service)
        .filter(Service.is_active.is_(True))
        .order_by(Service.name)
        .all()
    )


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    service_data: ServiceCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    existing = db.query(Service).filter(Service.name == service_data.name).first()
    if existing:
        if existing.is_active:
            raise HTTPException(status_code=409, detail="A service with this name already exists.")
        existing.description = service_data.description
        existing.image_url = service_data.image_url
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing

    service = Service(**service_data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.put("/{service_id}", response_model=ServiceResponse)
def update_service(
    service_id: int,
    service_data: ServiceUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    service = db.query(Service).filter(Service.id == service_id, Service.is_active.is_(True)).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    for field, value in service_data.model_dump(exclude_unset=True).items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    service_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    service = db.query(Service).filter(Service.id == service_id, Service.is_active.is_(True)).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    service.is_active = False
    db.commit()