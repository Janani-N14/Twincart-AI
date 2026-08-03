"""Campaign Poster Generator Agent.

Generates visual marketing posters using Stable Diffusion based on:
- Campaign copy from the campaign generator
- Regional/cultural context from the twin
- Color schemes and visual styles from banner briefs

This is a LangGraph node that produces base64-encoded images or file paths.
"""
import logging
from pathlib import Path

from app.graph.state import TwinAIState
from app.core.exceptions import AgentExecutionError

try:
    from app.ml.image_generation import PosterGenerator
    _POSTER_AVAILABLE = True
except ImportError:
    _POSTER_AVAILABLE = False

logger = logging.getLogger(__name__)

# Output directory for generated posters
_POSTERS_DIR = Path(__file__).resolve().parents[2] / "generated_posters"


def _build_poster_prompt(state: TwinAIState, campaign_line: str, banner_brief: str) -> str:
    """Build a detailed image generation prompt from campaign copy and context.

    Combines:
    - Campaign copy (what to say)
    - Banner brief (visual style)
    - Regional cultural elements
    """
    region_id = state.get("region_id", "")
    trends = ", ".join(state.get("trends") or [])
    weather = state.get("weather_signal", "")

    prompt = (
        f"Professional e-commerce marketing poster. Campaign: '{campaign_line}'. "
        f"Visual style: {banner_brief}. "
        f"Trending products: {trends}. "
        f"Context: {weather}. "
        f"High quality, vibrant colors, Indian aesthetic, text-overlay ready. "
        f"Aspect ratio 9:16 (mobile-optimized)."
    )
    return prompt


def run(state: TwinAIState) -> dict:
    """LangGraph node: generate campaign posters using Stable Diffusion.

    Requires ML dependencies: pip install -r requirements_ml.txt
    """
    if not _POSTER_AVAILABLE:
        logger.warning("[poster_generator] ML dependencies not installed; skipping poster generation")
        return {
            "poster_images": [],
            "explanation_log": ["Poster generation skipped (ML dependencies not installed)"],
        }

    region_id = state.get("region_id", "unknown")
    campaign_copy = state.get("campaign_copy") or []
    banner_briefs = state.get("banner_briefs") or []

    if not campaign_copy:
        logger.info("[poster_generator] %s → no campaign copy; skipping", region_id)
        return {
            "poster_images": [],
            "explanation_log": ["No campaign copy available for poster generation"],
        }

    try:
        # Initialize generator (lazy loads model on first call)
        generator = PosterGenerator(
            model_id="stabilityai/stable-diffusion-xl-base-1.0",  # Lighter than SD 3.5
            device="auto",
            use_half_precision=True,
        )

        _POSTERS_DIR.mkdir(parents=True, exist_ok=True)
        poster_paths = []

        for i, copy_line in enumerate(campaign_copy[:2]):  # Limit to 2 posters per region to save compute
            brief = banner_briefs[i] if i < len(banner_briefs) else "vibrant, eye-catching"
            prompt = _build_poster_prompt(state, copy_line, brief)

            logger.info("[poster_generator] %s → generating poster %d: %.40s...", region_id, i + 1, prompt)

            try:
                image = generator.generate(
                    prompt=prompt,
                    height=768,
                    width=512,
                    num_steps=20,  # Faster inference
                    guidance_scale=7.5,
                )

                # Save poster
                poster_filename = f"{region_id}_campaign_{i+1}.png"
                poster_path = _POSTERS_DIR / poster_filename
                generator.save_poster(image, poster_path)
                poster_paths.append(str(poster_path))

                logger.info("[poster_generator] Saved: %s", poster_path)
            except Exception as e:
                logger.error("[poster_generator] Failed to generate poster %d: %s", i + 1, e)
                continue

        return {
            "poster_images": poster_paths,
            "explanation_log": [
                f"Poster Generator ({region_id}): generated {len(poster_paths)} posters "
                f"({', '.join(Path(p).name for p in poster_paths[:2])})"
            ],
        }

    except Exception as exc:
        logger.error("[poster_generator] failed for %s: %s", region_id, exc)
        # Don't raise — poster generation is optional; pipeline can continue
        return {
            "poster_images": [],
            "explanation_log": [f"Poster generation error: {str(exc)[:80]}"],
        }
