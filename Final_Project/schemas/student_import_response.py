from typing import Annotated

from pydantic import BaseModel, Field

from schemas import StudentResponse


class ImportErrorDetails(BaseModel):
    row: Annotated[int, Field(title="Row number in CSV file", description="Row number in CSV file")]
    data: Annotated[dict, Field(title="Raw CSV data", description="Raw CSV data")]
    error: Annotated[str, Field(title="Error detail", description="Error detail")]


class StudentImportResponse(BaseModel):
    total: Annotated[int, Field(title="Total records", description="Total records")]
    success_count: Annotated[int, Field(title="Number of success records", description="Number of success records")]
    failed_count: Annotated[int, Field(title="Number of fail records", description="Number of fail records")]
    success: Annotated[list[StudentResponse], Field(title="Success data", description="Success data")]
    failed: Annotated[list[ImportErrorDetails], Field(title="Failed data", description="Failed data")]
