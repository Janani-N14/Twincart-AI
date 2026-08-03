"""Banner Studio Agent.

Produces structured visual banner briefs (headline, subtext, CTA, style)
for each campaign copy line.  Uses the large model — generative task.
"""
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.llm import get_llm
from app.core.exceptions import AgentExecutionError
from app.graph.state import TwinAIState
from app.twins.regional_twin import regional_twin_store

logger = logging.getLogger(__name__)

_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are TwinAI's Banner Studio agent. "
        "For each campaign copy line, write a concise visual banner brief. "
        "Respond ONLY with a valid JSON array of objects, each with keys: "
        '"headline" (≤8 words), "subtext" (≤15 words), "cta" (≤4 words), '
        '"visual_style" (colour palette + imagery hint, ≤12 words). '
        "One object per campaign line, in the same order. No other text.",
    ),
    (
        "human",
        "region_id:{region_id}\n"
        "state:{state}\n"
        "campaign_copy_lines:{copy_lines}\n"
        "weather_festival_signal:{weather}\n"
        "top_trends:{trends}",
    ),
])

_chain = _PROMPT | get_llm(temperature=0.6, fast=False) | JsonOutputParser()


def run(state: TwinAIState) -> dict:
    """LangGraph node: generate banner briefs for each campaign copy line."""
    region_id = state["region_id"]
    try:
        twin = regional_twin_store.get(region_id)
        copy_lines = state.get("campaign_copy") or []

        if not copy_lines:
            return {
                "banner_briefs": [],
                "explanation_log": [f"Banner Studio ({region_id}): no campaign copy to brief."],
            }

        raw_briefs: list[dict] = _chain.invoke({
            "region_id": region_id,
            "state": twin.state,
            "copy_lines": "\n".join(f"- {line}" for line in copy_lines),
            "weather": state.get("weather_signal") or "no special signal",
            "trends": ", ".join(state.get("trends") or []),
        })

        # Flatten to list of strings for the state (keep full dicts accessible via explanation)
        if isinstance(raw_briefs, list):
            briefs_text = [
                f"{b.get('headline', '')} | {b.get('subtext', '')} | CTA: {b.get('cta', '')} | Style: {b.get('visual_style', '')}"
                for b in raw_briefs
                if isinstance(b, dict)
            ]
        else:
            briefs_text = [str(raw_briefs)]

        logger.info("[banner_studio] %s → %d briefs", region_id, len(briefs_text))
        return {
            "banner_briefs": briefs_text,
            "explanation_log": [
                f"Banner Studio ({region_id}): created {len(briefs_text)} banner briefs."
            ],
        }
    except Exception as exc:
        logger.error("[banner_studio] failed for %s: %s", region_id, exc)
        raise AgentExecutionError("banner_studio", str(exc)) from exc
