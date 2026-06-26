import json
import re

from langchain_openai import ChatOpenAI
from pydantic import ValidationError

from app.config import load_prompt, settings
from app.schemas import ComplianceSummaryData
from app.utils.logging import get_logger

logger = get_logger(__name__)


def _extract_json(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text)


def summarize(text: str) -> ComplianceSummaryData:
    system_prompt, user_template = load_prompt("summary")
    prompt = user_template.format(document_text=text[: settings.summary_max_chars])

    llm = ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key or None,
        temperature=0.2,
    )
    logger.info("Generating compliance summary")
    response = llm.invoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
    )

    try:
        payload = _extract_json(str(response.content))
        return ComplianceSummaryData.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.warning("Summary JSON parse failed, falling back to overview only: %s", exc)
        return ComplianceSummaryData(
            overview=str(response.content).strip(),
            missing_information=["Structured summary parsing failed. Review the overview text."],
        )
