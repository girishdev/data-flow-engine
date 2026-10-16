
from zipfile import BadZipFile

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    Depends
)
from openpyxl.utils.exceptions import InvalidFileException

from app.schemas.excel import ExcelPreviewResponse
from app.services.excel_service import (
    ExcelValidationError,
    extract_excel_data
)

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.automation import AutomationUploadResponse
from app.services.automation_service import (
    UserNotFoundError,
    save_automation
)


router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post(
    "/files/preview",
    response_model=ExcelPreviewResponse
)
async def preview_excel(
    file: UploadFile = File(...),
    custom_name: str = Form(...)
):
    name = custom_name.strip()

    # Validate custom name
    if not name or len(name) > 100:
        raise HTTPException(
            status_code=400,
            detail="Custom name must contain 1-100 characters"
        )

    # Validate filename extension
    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are allowed"
        )

    # Read Excel file
    try:
        content = await file.read(MAX_FILE_SIZE + 1)
    finally:
        await file.close()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 5 MB"
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    try:
        result = extract_excel_data(content)

    except ExcelValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except (BadZipFile, InvalidFileException, ValueError, KeyError, OSError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted Excel file"
        ) from exc

    return ExcelPreviewResponse(
        custom_name=name,
        file_name=file.filename,
        sheet_name=result["sheet_name"],
        total_records=result["total_records"],
        data=result["data"]
    )


@router.post(
    "/files/upload",
    response_model=AutomationUploadResponse,
    status_code=201
)
def upload_and_store_excel(
    file: UploadFile = File(...),
    user_id: int = Form(...),
    custom_name: str = Form(...),
    db: Session = Depends(get_db)
):
    name = custom_name.strip()

    if not name or len(name) > 100:
        raise HTTPException(
            status_code=400,
            detail="Custom name must contain 1-100 characters"
        )

    if not file.filename or not file.filename.lower().endswith(".xlsx"):
        raise HTTPException(
            status_code=400,
            detail="Only .xlsx files are allowed"
        )

    try:
        content = file.file.read(MAX_FILE_SIZE + 1)
    finally:
        file.file.close()

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds 5 MB"
        )

    if not content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty"
        )

    try:
        result = extract_excel_data(content)

    except ExcelValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    except (BadZipFile, InvalidFileException, ValueError, KeyError, OSError) as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid or corrupted Excel file"
        ) from exc

    # Store custom name and extracted Excel data as JSON
    json_data = {
        "custom_name": name,
        **result
    }

    try:
        request_id = save_automation(
            db=db,
            user_id=user_id,
            file_name=file.filename,
            excel_data=json_data
        )

    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc)
        ) from exc

    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database operation failed"
        ) from exc

    return AutomationUploadResponse(
        request_id=request_id,
        user_id=user_id,
        file_name=file.filename,
        total_records=result["total_records"],
        message="Excel data stored successfully"
    )
