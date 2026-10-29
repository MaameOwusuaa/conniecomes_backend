from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies.user_dependencies import get_user_service
from app.services.user_service import UserService
from app.schemas.user import UserLogin
from app.schemas.token import Token


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/admin/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
)
def login_admin(
    credentials: UserLogin,
    service: UserService = Depends(get_user_service),
):
    try:
        return service.login_admin(credentials)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )