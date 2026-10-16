
from pydantic import BaseModel


class AutomationUploadResponse(BaseModel):
    request_id: str
    user_id: int
    file_name: str
    total_records: int
    message: str
