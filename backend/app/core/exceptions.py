"""Custom exception hierarchy for TwinAI.

All domain exceptions inherit from TwinAIError so callers can catch
the whole family with a single ``except TwinAIError`` clause while
still being able to handle specific cases when needed.
"""


class TwinAIError(Exception):
    """Base class for all TwinAI application errors."""


class RegionNotFoundError(TwinAIError):
    """Raised when a requested region_id does not exist in the twin store."""

    def __init__(self, region_id: str) -> None:
        super().__init__(f"Region '{region_id}' not found in the twin store.")
        self.region_id = region_id


class SegmentNotFoundError(TwinAIError):
    """Raised when a requested segment_id does not exist."""

    def __init__(self, segment_id: str) -> None:
        super().__init__(f"Segment '{segment_id}' not found.")
        self.segment_id = segment_id


class AgentExecutionError(TwinAIError):
    """Raised when an agent node fails during the LangGraph pipeline."""

    def __init__(self, agent_name: str, reason: str) -> None:
        super().__init__(f"Agent '{agent_name}' failed: {reason}")
        self.agent_name = agent_name
        self.reason = reason


class LLMError(TwinAIError):
    """Raised when the Groq LLM call fails after all retries."""


class SimulationError(TwinAIError):
    """Raised when the What-If simulation engine encounters an invalid input."""
