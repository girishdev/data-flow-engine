
from io import BytesIO

from openpyxl import Workbook

from app.services.excel_service import REQUIRED_HEADERS


def generate_excel(excel_data: dict) -> BytesIO:

    workbook = Workbook()
    sheet = workbook.active

    sheet.title = excel_data.get("sheet_name") or "Signals"

    # Write Excel headers
    sheet.append(REQUIRED_HEADERS)

    # Write signal records
    for record in excel_data["data"]:
        row = [
            record.get(header)
            for header in REQUIRED_HEADERS
        ]

        # Prevent formula injection from stored text
        row = [
            "'" + value if isinstance(value, str)
            and value.startswith(("=", "+", "-", "@"))
            else value
            for value in row
        ]

        sheet.append(row)

    output = BytesIO()
    workbook.save(output)
    workbook.close()

    output.seek(0)

    return output
