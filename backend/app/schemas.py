from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None


class UploadResponse(BaseModel):
    document_id: UUID
    filename: str
    page_count: int
    chunk_count: int
    message: str = "Document uploaded and indexed successfully."


class DocumentInfo(BaseModel):
    document_id: UUID
    filename: str
    page_count: int | None = None
    chunk_count: int | None = None


class ChatRequest(BaseModel):
    document_id: UUID
    question: str = Field(..., min_length=1, max_length=2000)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Question cannot be empty.")
        return cleaned


class SourceChunk(BaseModel):
    page: int
    chunk: int
    excerpt: str
    section: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceChunk] = Field(default_factory=list)
    found_in_document: bool = True


class SummaryRequest(BaseModel):
    document_id: UUID


class ComplianceSummaryData(BaseModel):
    overview: str
    key_obligations: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class SummaryResponse(BaseModel):
    document_id: UUID
    summary: ComplianceSummaryData
