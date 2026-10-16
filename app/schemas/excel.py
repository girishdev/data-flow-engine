
from pydantic import BaseModel


class ExcelPreviewResponse(BaseModel):
    custom_name: str
    file_name: str
    sheet_name: str
    total_records: int
    data: list[dict[str, str | int | float | bool | None]]
