
from datetime import datetime, timezone
from secrets import token_hex

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.database_models import User, DataAutomation


class UserNotFoundError(Exception):
    pass


def generate_request_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%d%H%M%S%f"
    )

    random_suffix = token_hex(4).upper()

    return f"DFE-{timestamp}-{random_suffix}"


def save_automation(
    db: Session,
    user_id: int,
    file_name: str,
    excel_data: dict
) -> str:

    user = db.get(User, user_id)

    if user is None:
        raise UserNotFoundError("User not found")

    request_id = generate_request_id()

    upload = DataAutomation(
        user_id=user_id,
        file_name=file_name,
        request_id=request_id,
        data=excel_data
    )

    try:
        db.add(upload)
        db.commit()

        return request_id

    except Exception:
        db.rollback()
        raise


def get_automation_by_request_id(
    db: Session,
    request_id: str
) -> DataAutomation | None:

    statement = select(DataAutomation).where(
        DataAutomation.request_id == request_id
    )

    return db.scalars(statement).first()
