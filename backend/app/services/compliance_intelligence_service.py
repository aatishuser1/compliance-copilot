import json
import re
from typing import Any

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from app.config import load_prompt, settings
from app.schemas import (
    ComplianceObligation,
    CompliancePenalty,
    ComplianceRisk,
    ComplianceSummaryData,
    Effort,
    Priority,
    RecommendedAction,
    RiskLevel,
    Severity,
    SourceReference,
)
from app.services.retrieval_service import retrieve_for_compliance
from app.utils.logging import get_logger

logger = get_logger(__name__)

_REF_PATTERN = re.compile(r"^REF-(\d+)$")


def _extract_json(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


def _format_context_with_refs(
    documents: list[Document],
    *,
    max_chars: int,
) -> tuple[str, dict[str, Document]]:
    """Format chunks with REF labels and build a lookup map."""
    ref_map: dict[str, Document] = {}
    sections: list[str] = []
    total_chars = 0

    for index, document in enumerate(documents, start=1):
        ref_id = f"REF-{index}"
        ref_map[ref_id] = document
        page = document.metadata.get("page", "?")
        chunk = document.metadata.get("chunk", "?")
        section = document.metadata.get("section_heading") or document.metadata.get(
            "parent_section"
        )
        label = f"[{ref_id} | Page {page} | Chunk {chunk}"
        if section:
            label += f" | {section}"
        label += "]"
        block = f"{label}\n{document.page_content.strip()}"
        if total_chars + len(block) > max_chars:
            break
        sections.append(block)
        total_chars += len(block)

    return "\n\n---\n\n".join(sections), ref_map


def _resolve_source_refs(
    source_refs: list[str],
    ref_map: dict[str, Document],
) -> list[SourceReference]:
    sources: list[SourceReference] = []
    seen: set[tuple[int, int | None]] = set()

    for ref in source_refs:
        if not _REF_PATTERN.match(ref):
            continue
        document = ref_map.get(ref)
        if document is None:
            continue
        page = int(document.metadata.get("page", 0))
        chunk = int(document.metadata.get("chunk", 0))
        key = (page, chunk)
        if key in seen:
            continue
        seen.add(key)
        section = document.metadata.get("section_heading") or document.metadata.get(
            "parent_section"
        )
        sources.append(
            SourceReference(
                page=page,
                chunk=chunk,
                section=section or None,
                excerpt=document.page_content[:200].strip(),
            )
        )
    return sources


def _invoke_llm(system_prompt: str, user_prompt: str, *, temperature: float) -> str:
    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key or None,
        temperature=temperature,
    )
    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    return str(response.content)


def _extract_compliance_facts(
    context: str,
    ref_map: dict[str, Document],
) -> dict[str, Any]:
    system_prompt, user_template = load_prompt("compliance_extract")
    prompt = user_template.format(context=context)
    raw = _invoke_llm(system_prompt, prompt, temperature=0.1)
    payload = _extract_json(raw)

    obligations: list[ComplianceObligation] = []
    for item in payload.get("obligations", []):
        sources = _resolve_source_refs(item.get("source_refs", []), ref_map)
        if not sources:
            continue
        obligations.append(
            ComplianceObligation(
                id=item.get("id", f"OBL-{len(obligations) + 1}"),
                title=item.get("title", "Untitled obligation"),
                description=item.get("description", ""),
                priority=Priority(item.get("priority", "medium")),
                category=item.get("category"),
                deadline=item.get("deadline"),
                sources=sources,
            )
        )

    risks: list[ComplianceRisk] = []
    for item in payload.get("risks", []):
        sources = _resolve_source_refs(item.get("source_refs", []), ref_map)
        if not sources:
            continue
        risks.append(
            ComplianceRisk(
                id=item.get("id", f"RSK-{len(risks) + 1}"),
                title=item.get("title", "Untitled risk"),
                description=item.get("description", ""),
                severity=Severity(item.get("severity", "medium")),
                likelihood=item.get("likelihood"),
                related_obligation_ids=item.get("related_obligation_ids", []),
                sources=sources,
            )
        )

    penalties: list[CompliancePenalty] = []
    for item in payload.get("penalties", []):
        sources = _resolve_source_refs(item.get("source_refs", []), ref_map)
        if not sources:
            continue
        penalties.append(
            CompliancePenalty(
                id=item.get("id", f"PEN-{len(penalties) + 1}"),
                description=item.get("description", ""),
                amount_or_range=item.get("amount_or_range"),
                penalty_type=item.get("penalty_type"),
                trigger=item.get("trigger"),
                related_obligation_ids=item.get("related_obligation_ids", []),
                sources=sources,
            )
        )

    return {
        "document_type": payload.get("document_type"),
        "regulatory_framework": payload.get("regulatory_framework"),
        "obligations": obligations,
        "risks": risks,
        "penalties": penalties,
    }


def _synthesize_intelligence(
    context: str,
    extracted: dict[str, Any],
) -> dict[str, Any]:
    system_prompt, user_template = load_prompt("compliance_synthesize")
    extracted_summary = {
        "document_type": extracted.get("document_type"),
        "regulatory_framework": extracted.get("regulatory_framework"),
        "obligations": [
            {
                "id": o.id,
                "title": o.title,
                "description": o.description,
                "priority": o.priority.value,
            }
            for o in extracted["obligations"]
        ],
        "risks": [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "severity": r.severity.value,
            }
            for r in extracted["risks"]
        ],
        "penalties": [
            {
                "id": p.id,
                "description": p.description,
                "amount_or_range": p.amount_or_range,
            }
            for p in extracted["penalties"]
        ],
    }
    prompt = user_template.format(
        extracted_facts=json.dumps(extracted_summary, indent=2),
        context=context[:8000],
    )
    raw = _invoke_llm(system_prompt, prompt, temperature=0.2)
    return _extract_json(raw)


def _derive_risk_level(
    synthesis_risk_level: str | None,
    risks: list[ComplianceRisk],
    penalties: list[CompliancePenalty],
) -> RiskLevel:
    if synthesis_risk_level:
        try:
            return RiskLevel(synthesis_risk_level)
        except ValueError:
            pass

    severity_rank = {
        Severity.CRITICAL: 4,
        Severity.HIGH: 3,
        Severity.MEDIUM: 2,
        Severity.LOW: 1,
    }
    max_severity = max(
        (severity_rank.get(r.severity, 2) for r in risks),
        default=0,
    )
    if penalties and max_severity >= 3:
        return RiskLevel.CRITICAL
    if max_severity >= 4:
        return RiskLevel.CRITICAL
    if max_severity >= 3 or penalties:
        return RiskLevel.HIGH
    if max_severity >= 2:
        return RiskLevel.MEDIUM
    return RiskLevel.LOW


def analyze_document(document_id: str) -> ComplianceSummaryData:
    """RAG-grounded multi-pass compliance intelligence pipeline."""
    documents = retrieve_for_compliance(document_id)
    if not documents:
        return ComplianceSummaryData(
            overview="Insufficient document content was retrieved to produce a compliance analysis.",
            missing_information=[
                "The document could not be indexed or contains no extractable compliance content."
            ],
            analysis_notes="Retrieval returned no relevant chunks. Try re-uploading the document.",
        )

    context, ref_map = _format_context_with_refs(
        documents,
        max_chars=settings.compliance_max_context_chars,
    )
    logger.info(
        "Compliance analysis for %s: %d chunks, %d chars of context",
        document_id,
        len(ref_map),
        len(context),
    )

    try:
        extracted = _extract_compliance_facts(context, ref_map)
        synthesis = _synthesize_intelligence(context, extracted)

        actions: list[RecommendedAction] = []
        for item in synthesis.get("recommended_actions", []):
            actions.append(
                RecommendedAction(
                    id=item.get("id", f"ACT-{len(actions) + 1}"),
                    title=item.get("title", "Recommended action"),
                    description=item.get("description", ""),
                    priority=Priority(item.get("priority", "medium")),
                    effort=Effort(item.get("effort", "medium")),
                    related_risk_ids=item.get("related_risk_ids", []),
                    related_obligation_ids=item.get("related_obligation_ids", []),
                )
            )

        return ComplianceSummaryData(
            overview=synthesis.get("overview", "Compliance analysis complete."),
            document_type=extracted.get("document_type"),
            regulatory_framework=extracted.get("regulatory_framework"),
            risk_level=_derive_risk_level(
                synthesis.get("risk_level"),
                extracted["risks"],
                extracted["penalties"],
            ),
            obligations=extracted["obligations"],
            risks=extracted["risks"],
            penalties=extracted["penalties"],
            missing_information=synthesis.get("missing_information", []),
            recommended_actions=actions,
            analysis_notes=synthesis.get("analysis_notes"),
        )
    except (json.JSONDecodeError, ValidationError, KeyError, ValueError) as exc:
        logger.warning("Compliance intelligence parse failed for %s: %s", document_id, exc)
        return ComplianceSummaryData(
            overview="Compliance analysis encountered a parsing error. Partial results may be unavailable.",
            missing_information=["Structured compliance output could not be fully parsed."],
            analysis_notes=str(exc),
        )
