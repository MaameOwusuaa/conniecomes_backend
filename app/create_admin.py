from getpass import getpass

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repositories import UserRepository


def main() -> None:
    password = getpass(f"Set password for {settings.ADMIN_EMAIL}: ")
    confirmation = getpass("Confirm admin password: ")
    if len(password) < 8 or password != confirmation:
        raise SystemExit("Passwords must match and be at least 8 characters.")

    with SessionLocal() as db:
        repository = UserRepository(db)
        admin = repository.get_by_email(settings.ADMIN_EMAIL)
        if admin is None:
            admin = User(
                first_name="Admin",
                last_name="Account",
                email=settings.ADMIN_EMAIL,
                hashed_password=hash_password(password),
                is_admin=True,
                is_active=True,
                email_verified=True,
            )
            db.add(admin)
        else:
            admin.hashed_password = hash_password(password)
            admin.is_admin = True
            admin.is_active = True
            admin.email_verified = True

        db.commit()

    print(f"Administrator account configured for {settings.ADMIN_EMAIL}.")


if __name__ == "__main__":
    main()