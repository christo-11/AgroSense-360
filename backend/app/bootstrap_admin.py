"""Create or reset a configured admin with a one-time generated password."""

import os
import secrets
import sys

from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal
from app.models import User
from app.security import hash_password


def main() -> None:
    settings = get_settings()
    email = os.environ.get("ADMIN_BOOTSTRAP_EMAIL", "").strip().casefold()
    reset = "--reset" in sys.argv[1:]
    if not email or email not in settings.agricultural_admin_email_set:
        raise SystemExit(
            "Set ADMIN_BOOTSTRAP_EMAIL to an address already listed in AGRICULTURAL_ADMIN_EMAILS."
        )
    if settings.public_demo_mode:
        raise SystemExit("Admin bootstrap is disabled in public demo mode.")
    if not settings.auth_configured:
        raise SystemExit("Configure a secure JWT_SECRET before bootstrapping an admin.")
    if SessionLocal is None:
        raise SystemExit("DATABASE_URL is not configured.")

    password = secrets.token_urlsafe(32)
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email))
        if user is not None and not reset:
            raise SystemExit("This admin account already exists. Use --reset to issue a new one-time password.")
        if user is None:
            user = User(email=email, password_hash=hash_password(password), must_change_password=True)
            db.add(user)
        else:
            user.password_hash = hash_password(password)
            user.must_change_password = True
        db.commit()

    print("Admin username: " + email)
    print("Temporary password (shown once): " + password)
    print("Sign in immediately; AgroSense will require a new password before other use.")


if __name__ == "__main__":
    main()
