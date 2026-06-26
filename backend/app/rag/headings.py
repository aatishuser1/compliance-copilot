import re

from langchain_core.documents import Document

KNOWN_HEADINGS = [
    "Core Requirements",
    "Document Upload & Processing",
    "Document Upload",
    "AI-Powered Question Answering (RAG)",
    "AI-Powered Question Answering",
    "Compliance Risk Summary",
    "User Interface",
    "Backend APIs",
    "Deployment",
    "Technical Expectations",
    "Submission Requirements",
    "Evaluation Criteria",
    "Architecture & System Design",
    "Code Quality & Engineering Practices",
    "Deployment & DevOps",
]

TOP_LEVEL_MARKERS = {
    "Objective",
    "Problem Statement",
    "Core Requirements",
    "Technical Expectations",
    "Submission Requirements",
    "Evaluation Criteria",
}

NUMBERED_SECTION = re.compile(r"^\d+\.\s+.+")
STOP_WORDS = {
    "what",
    "are",
    "the",
    "is",
    "a",
    "an",
    "how",
    "does",
    "do",
    "tell",
    "me",
    "about",
    "of",
    "in",
    "to",
    "and",
    "or",
    "for",
    "with",
    "from",
    "this",
    "that",
    "should",
    "can",
    "be",
}


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def significant_words(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", normalize(text))
    return {word for word in words if word not in STOP_WORDS and len(word) > 2}


def is_section_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("●"):
        return False

    normalized = normalize(stripped)
    if NUMBERED_SECTION.match(stripped):
        return True

    for heading in KNOWN_HEADINGS:
        if normalize(heading) == normalized:
            return True

    return normalized in {normalize(marker) for marker in TOP_LEVEL_MARKERS}


def split_page_into_sections(
    page_text: str,
    *,
    initial_parent: str | None = None,
) -> tuple[list[tuple[str, str | None, str]], str | None]:
    """Split a page into sections; carry parent context across pages."""
    lines = page_text.split("\n")
    sections: list[tuple[str, str | None, str]] = []
    current_heading = "Page Content"
    active_parent = initial_parent
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if not buffer:
            return
        text = "\n".join(buffer).strip()
        if text:
            parent = active_parent if current_heading != "Page Content" else initial_parent
            sections.append((current_heading, parent, text))
        buffer = []

    for line in lines:
        stripped = line.strip()
        if stripped and is_section_heading(stripped):
            flush()
            current_heading = stripped
            if normalize(stripped) in {normalize(marker) for marker in TOP_LEVEL_MARKERS}:
                active_parent = stripped
        else:
            buffer.append(line)

    flush()

    if not sections:
        sections = [("Page Content", initial_parent, page_text.strip())]

    return sections, active_parent


def heading_matches_query(query: str, heading: str) -> bool:
    query_words = significant_words(query)
    heading_words = significant_words(heading)
    if not query_words or not heading_words:
        return False

    overlap = query_words & heading_words
    if overlap == query_words or overlap == heading_words:
        return True
    if len(overlap) >= 2:
        return True
    return len(overlap) / len(query_words) >= 0.66


def partial_heading_overlap(query: str, heading: str) -> bool:
    query_words = significant_words(query)
    heading_words = significant_words(heading)
    overlap = query_words & heading_words
    return bool(overlap) and not heading_matches_query(query, heading)


def heading_match_boost(query: str, document: Document) -> float:
    boost = 0.0
    section_heading = str(document.metadata.get("section_heading", ""))
    parent_section = str(document.metadata.get("parent_section", ""))

    for label in (section_heading, parent_section):
        if not label:
            continue
        if heading_matches_query(query, label):
            boost = max(boost, 12.0)
        elif partial_heading_overlap(query, label):
            boost = max(boost, 6.0)

    content_lower = document.page_content.lower()
    for heading in KNOWN_HEADINGS:
        if heading.lower() not in content_lower:
            continue
        if heading_matches_query(query, heading):
            boost = max(boost, 10.0)
        elif partial_heading_overlap(query, heading):
            boost = max(boost, 4.0)

    return boost


def rerank_with_headings(
    query: str,
    results: list[tuple[Document, float]],
) -> list[tuple[Document, float]]:
    return sorted(
        results,
        key=lambda item: (-heading_match_boost(query, item[0]), item[1]),
    )
