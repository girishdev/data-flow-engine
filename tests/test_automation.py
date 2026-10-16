
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.services.automation_service import (
    generate_request_id,
    save_automation,
    UserNotFoundError
)


def test_request_id_uniqueness():
    first = generate_request_id()
    second = generate_request_id()

    assert first.startswith("DFE-")
    assert first != second
    assert len(first) <= 50


def test_successful_database_storage():
    db = MagicMock()
    db.get.return_value = MagicMock()

    request_id = save_automation(
        db=db,
        user_id=1,
        file_name="signals.xlsx",
        excel_data={"data": [{"signal_name": "S1"}]}
    )

    assert request_id.startswith("DFE-")
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.rollback.assert_not_called()

    stored_object = db.add.call_args.args[0]
    assert stored_object.user_id == 1
    assert stored_object.request_id == request_id


def test_user_not_found():
    db = MagicMock()
    db.get.return_value = None

    with pytest.raises(UserNotFoundError):
        save_automation(
            db=db,
            user_id=999,
            file_name="signals.xlsx",
            excel_data={"data": []}
        )

    db.add.assert_not_called()
    db.commit.assert_not_called()


def test_transaction_rollback():
    db = MagicMock()
    db.get.return_value = MagicMock()
    db.commit.side_effect = SQLAlchemyError("Commit failed")

    with pytest.raises(SQLAlchemyError):
        save_automation(
            db=db,
            user_id=1,
            file_name="signals.xlsx",
            excel_data={"data": []}
        )

    db.rollback.assert_called_once()
