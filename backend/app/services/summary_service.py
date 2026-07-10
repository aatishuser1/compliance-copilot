from app.schemas import ComplianceSummaryData
from app.services.compliance_intelligence_service import analyze_document


def summarize(document_id: str) -> ComplianceSummaryData:
    """Generate RAG-grounded structured compliance intelligence for a document."""
    return analyze_document(document_id)
