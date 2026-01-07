from pydantic import BaseModel, Field

from schemas import StudentResponse


class ImportErrorDetails(BaseModel):
    row: int = Field(title="Row number in CSV file", description="Row number in CSV file")
    data: dict = Field(title="Raw CSV data", description="Raw CSV data")
    error: str = Field(title="Error detail", description="Error detail")


class StudentImportResponse(BaseModel):
    total: int = Field(title="Total records", description="Total records")
    success_count: int = Field(title="Number of success records", description="Number of success records")
    failed_count: int = Field(title="Number of fail records", description="Number of fail records")
    success: list[StudentResponse] = Field(title="Success data", description="Success data")
    failed: list[ImportErrorDetails] = Field(title="Failed data", description="Failed data")
