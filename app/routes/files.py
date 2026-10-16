
from zipfile import BadZipFile

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile
)
from openpyxl.utils.exceptions import InvalidFileException

from app.schemas.excel import ExcelPreviewResponse
from app.services.excel_service import (
    ExcelValidationError,
    extract_excel_data
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
