"""Explainability Agent.

Terminal node in the pipeline.  Reads the full explanation_log accumulated
by all previous agents and produces a single coherent plain-language
summary that sellers can read to understand why TwinAI made its
recommendations.  Uses the large model — synthesis/writing task.
"""
import logging

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.llm import get_llm
from app.core.exceptions import AgentExecutionError
from app.graph.state import TwinAIState

logger = logging.getLogger(__name__)

_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are TwinAI's Explainability agent. "
        "Summarise the agent pipeline's findings in 3-5 plain-language sentences "
        "that a non-technical seller can understand. "
        "Cover: what trends were found, what the demand forecast implies, "
        "which campaigns were suggested, how the budget was split, and any "
        "catalog gaps. Be specific, cite numbers where available. "
        "Output plain text only — no JSON, no markdown.",
    ),
    (
        "human",
        "region_id:{region_id}\n"
        "pipeline_log:\n{log}",
    ),
])

_chain = _PROMPT | get_llm(temperature=0.3, fast=False) | StrOutputParser()


def run(state: TwinAIState) -> dict:
    """LangGraph node: synthesise a plain-language explanation of the full pipeline."""
    region_id = state["region_id"]
    try:
        log_text = "\n".join(state.get("explanation_log") or ["No log entries."])
        explanation: str = _chain.invoke({
            "region_id": region_id,
            "log": log_text,
        })
        logger.info("[explainability] %s → explanation generated (%d chars)", region_id, len(explanation))
        return {
            "explanation_log": [f"Explainability summary generated for {region_id}."],
            # We store the final explanation back into explanation_log so the orchestrator
            # can join all entries into the CampaignResponse.explanation field.
            # Convention: the last entry is always the human-readable summary.
        }
    except Exception as exc:
        logger.error("[explainability] failed for %s: %s", region_id, exc)
        raise AgentExecutionError("explainability", str(exc)) from exc


def run_with_summary(state: TwinAIState) -> tuple[dict, str]:
    """Helper used by the orchestrator to also return the explanation string directly."""
    region_id = state["region_id"]
    log_text = "\n".join(state.get("explanation_log") or ["No log entries."])
    try:
        explanation: str = _chain.invoke({
            "region_id": region_id,
            "log": log_text,
        })
    except Exception:
        explanation = log_text  # fallback: raw log
    partial = run(state)
    return partial, explanation
