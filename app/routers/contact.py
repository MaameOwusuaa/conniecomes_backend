from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.contact_message import ContactMessage
from app.schemas.contact_message import ContactMessageCreate, ContactMessageResponse


router = APIRouter(prefix="/contact-messages", tags=["Contact"])


@router.post("", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
def create_contact_message(
    message_data: ContactMessageCreate,
    db: Session = Depends(get_db),
):
    message = ContactMessage(
        name=message_data.name.strip(),
        email=str(message_data.email).strip(),
        message=message_data.message.strip(),
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
