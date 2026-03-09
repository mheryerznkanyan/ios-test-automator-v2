"""EnrichmentService — expands a brief test description into a precise test specification."""
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.prompts import ENRICHMENT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Descriptions shorter than this are always sent for enrichment.
# Longer ones are still enriched, but the original is preserved in metadata.
_MIN_ENRICH_LENGTH = 0


class EnrichmentService:
    """Uses the LLM to rewrite a vague test description into a precise specification.

    The LLM is injected at construction time (same instance as TestGenerator).
    """

    def __init__(self, llm):
        self._llm = llm

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type(Exception),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _invoke_llm(self, messages):
        return self._llm.invoke(messages)

    def enrich(self, description: str) -> dict:
        """Enrich a test description and return both versions.

        Args:
            description: Raw user-supplied test description.

        Returns:
            dict with keys:
                - ``original``  : the original description unchanged.
                - ``enriched``  : the LLM-expanded description.
                - ``used``      : always True (enrichment was attempted).
                - ``error``     : present only if enrichment failed; in that case
                                  ``enriched`` falls back to ``original``.
        """
        original = description.strip()

        messages = [
            SystemMessage(content=ENRICHMENT_SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Enrich this iOS test description:\n\n{original}\n\n"
                    "Return only the enriched description text."
                )
            ),
        ]

        try:
            logger.info("Enriching test description: %r", original[:80])
            response = self._invoke_llm(messages)
            enriched = response.content.strip()
            logger.info("Enriched description: %r", enriched[:120])
            return {"original": original, "enriched": enriched, "used": True}
        except Exception as exc:
            logger.error("Enrichment failed, using original description: %s", exc)
            return {
                "original": original,
                "enriched": original,
                "used": True,
                "error": str(exc),
            }
