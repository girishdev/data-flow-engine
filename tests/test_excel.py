
from io import BytesIO

from fastapi.testclient import TestClient
from openpyxl import Workbook

from app.main import app


client = TestClient(app)


def create_excel(headers=None):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Signals"

    if headers is None:
        headers = [
            "signal_name",
            "application",
            "signal_direction",
            "factor",
            "safety",
            "status",
            "description",
        ]

    sheet.append(headers)
    sheet.append([
        "signal_001",
        "Engine",
        "Input",
        1.5,
        True,
        "Active",
        "Test signal"
    ])

    output = BytesIO()
    workbook.save(output)
    workbook.close()

    return output.getvalue()


def upload_excel(filename, content):
    return client.post(
        "/api/files/preview",
        data={"custom_name": "Test Signals"},
        files={
            "file": (
                filename,
                content,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        }
    )


def test_valid_excel_upload():
    response = upload_excel(
        "signals.xlsx",
        create_excel()
    )

    assert response.status_code == 200

    result = response.json()

    assert result["total_records"] == 1
    assert result["sheet_name"] == "Signals"
    assert result["data"][0]["signal_name"] == "signal_001"
    assert result["data"][0]["factor"] == 1.5


def test_invalid_headers():
    response = upload_excel(
        "signals.xlsx",
        create_excel(headers=["invalid_header"])
    )

    assert response.status_code == 400


def test_invalid_extension():
    response = upload_excel(
        "signals.txt",
        b"invalid"
    )

    assert response.status_code == 400


def test_corrupted_excel():
    response = upload_excel(
        "signals.xlsx",
        b"not a valid Excel file"
    )

    assert response.status_code == 400


def test_file_too_large():
    response = upload_excel(
        "signals.xlsx",
        b"x" * (5 * 1024 * 1024 + 1)
    )

    assert response.status_code == 413
