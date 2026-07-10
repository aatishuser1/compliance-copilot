from enum import Enum
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


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Effort(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SourceReference(BaseModel):
    page: int
    chunk: int | None = None
    section: str | None = None
    excerpt: str | None = None


class ComplianceObligation(BaseModel):
    id: str
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    category: str | None = None
    deadline: str | None = None
    sources: list[SourceReference] = Field(default_factory=list)


class ComplianceRisk(BaseModel):
    id: str
    title: str
    description: str
    severity: Severity = Severity.MEDIUM
    likelihood: str | None = None
    related_obligation_ids: list[str] = Field(default_factory=list)
    sources: list[SourceReference] = Field(default_factory=list)


class CompliancePenalty(BaseModel):
    id: str
    description: str
    amount_or_range: str | None = None
    penalty_type: str | None = None
    trigger: str | None = None
    related_obligation_ids: list[str] = Field(default_factory=list)
    sources: list[SourceReference] = Field(default_factory=list)


class RecommendedAction(BaseModel):
    id: str
    title: str
    description: str
    priority: Priority = Priority.MEDIUM
    effort: Effort = Effort.MEDIUM
    related_risk_ids: list[str] = Field(default_factory=list)
    related_obligation_ids: list[str] = Field(default_factory=list)


class ComplianceSummaryData(BaseModel):
    overview: str
    document_type: str | None = None
    regulatory_framework: str | None = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    obligations: list[ComplianceObligation] = Field(default_factory=list)
    risks: list[ComplianceRisk] = Field(default_factory=list)
    penalties: list[CompliancePenalty] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    recommended_actions: list[RecommendedAction] = Field(default_factory=list)
    analysis_notes: str | None = None


class SummaryResponse(BaseModel):
    document_id: UUID
    summary: ComplianceSummaryData
