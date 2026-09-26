"""Campaign Generation Agent for TwinCart AI.

Generates bilingual hyperlocal advertising copy:
- English headline, body, and CTA
- Vernacular local-language headline, body, and CTA (Tamil, Hindi, Telugu, Marathi, etc.)
- Tailored to regional twin signals, active festival calendar, and customer segment personas.
- Uses versioned prompt from app/prompts/campaign_prompt.txt.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

from app.core.llm import get_llm
from app.graph.state import TwinAIState
from app.twins.regional_twin import regional_twin_store
from app.twins.segment_twin import segment_twin_store

logger = logging.getLogger(__name__)

PROMPT_FILE = Path(__file__).resolve().parents[1] / "prompts" / "campaign_prompt.txt"

# Vernacular fallback dictionary for robust offline execution
VERNACULAR_FALLBACKS = {
    "Tamil": {
        "headline": "மதுரை & தமிழகத்திற்கான சிறப்பு திருவிழா தள்ளுபடி!",
        "body": "அசல் தரம், நேரடி உற்பத்தியாளர் விலை. சிறந்த காட்டன் மற்றும் ஆடைகள் இப்போது 60% வரை தள்ளுபடியில்.",
        "cta": "இப்போதே வாங்கவும்",
    },
    "Hindi": {
        "headline": "त्योहारी सीजन की सबसे बड़ी सेल — सीधे आपके शहर में!",
        "body": "बेहतरीन क्वालिटी और किफायती दाम। एथनिक वियर और होम डेकोर पर पाएं 60% तक की भारी छूट।",
        "cta": "अभी खरीदें",
    },
    "Telugu": {
        "headline": "మీ ప్రాంతం కోసం ప్రత్యేక పండుగ ఆఫర్లు!",
        "body": "నాణ్యమైన ఉత్పత్తులు, నేరుగా హోల్‌సేల్ ధరలకే. 60% వరకు భారీ తగ్గింపుతో ఇప్పుడే ఆర్డర్ చేయండి.",
        "cta": "ఇప్పుడే కొనండి",
    },
    "Marathi": {
        "headline": "उत्सवी हंगामातील सर्वात मोठी सूट — थेट तुमच्या दारात!",
        "body": "उत्कृष्ट दर्जा आणि बजेट-फ्रेंडली किमती. एथनिक फॅशन आणि घरगुती वस्तूंवर मिळवा ६०% पर्यंत सूट.",
        "cta": "आताच खरेदी करा",
    },
    "Bengali": {
        "headline": "উৎসবের সেরা অফার — আপনার শহরের নিজস্ব স্টোর থেকে!",
        "body": "সেরা কোয়ালিটি এবং সরাসরি প্রস্তুতকারকের দাম। এথনিক পোশাক ও গহনায় পান ৬০% পর্যন্ত ছাড়।",
        "cta": "এখনই অর্ডার করুন",
    },
    "Malayalam": {
        "headline": "നിങ്ങളുടെ നാടിനായി പ്രത്യേക ഉത്സവ വിലക്കുറവ്!",
        "body": "മികച്ച ഗുണനിലവാരവും നേരിട്ടുള്ള നിർമ്മാതാക്കളുടെ വിലയും. 60% വരെ ആകർഷകമായ ഓഫറുകൾ ഇപ്പോൾ ലഭ്യമാണ്.",
        "cta": "ഇപ്പോൾ വാങ്ങൂ",
    },
    "Kannada": {
        "headline": "ನಿಮ್ಮ ನಗರಕ್ಕಾಗಿ ವಿಶೇಷ ಹಬ್ಬದ ರಿಯಾಯಿತಿ!",
        "body": "ಉತ್ತಮ ಗುಣಮಟ್ಟ, ನೇರ ಉತ್ಪಾದಕರ ಬೆಲೆ. ಎಥ್ನಿಕ್ ಬಟ್ಟೆಗಳು ಮತ್ತು ಗೃಹೋಪಯೋಗಿ ವಸ್ತುಗಳ ಮೇಲೆ 60% ವರೆಗೆ ರಿಯಾಯಿತಿ.",
        "cta": "ಈಗಲೇ ಖರೀದಿಸಿ",
    },
    "Gujarati": {
        "headline": "તહેવારોની સીઝનની સૌથી મોટી ધમાકા ઓફર!",
        "body": "શ્રેષ્ઠ ક્વોલિટી અને હોલસેલ ભાવ. એથનિક ફેશન અને એક્સેસરીઝ પર મેળવો 60% સુધીનું ડિસ્કાઉન્ટ.",
        "cta": "હમણાં ખરીદો",
    },
}


def load_prompt_template() -> PromptTemplate:
    """Load versioned prompt template from disk."""
    if PROMPT_FILE.exists():
        template_text = PROMPT_FILE.read_text(encoding="utf-8")
        return PromptTemplate.from_template(template_text)
    # Fallback inline template
    return PromptTemplate.from_template(
        "Generate a campaign in English and {target_language} for {state} ({category}). "
        "Return JSON with headline_en, body_en, headline_vernacular, body_vernacular, call_to_action_en, call_to_action_vernacular."
    )


def run(state: TwinAIState) -> dict:
    """LangGraph node: generate bilingual hyperlocal campaign copy."""
    region_id = state.get("region_id", "TN-01")
    twin = regional_twin_store.get(region_id)
    segment_id = state.get("segment_id", "students")
    seg = segment_twin_store.get_or_none(segment_id)

    segment_label = seg.label if seg else "Value Shoppers"
    age_range = seg.age_range if seg else "18-45"
    budget_range = seg.budget_range if seg else "₹500 - ₹2,500"

    category = state.get("category", twin.top_categories[0] if twin.top_categories else "apparel")
    trends = state.get("trends", [f"{category} festive deals", "cotton essentials"])
    point_forecast = float(state.get("point_forecast", 45000.0))
    active_festival = twin.active_festivals[0] if twin.active_festivals else "Grand Festive Season"
    target_lang = twin.languages[0] if twin.languages else "Hindi"

    try:
        prompt_tmpl = load_prompt_template()
        chain = prompt_tmpl | get_llm(temperature=0.4, fast=False) | JsonOutputParser()

        payload = {
            "state": twin.state,
            "city": twin.city or f"{twin.state} Hub",
            "region_id": region_id,
            "segment_label": segment_label,
            "age_range": age_range,
            "budget_range": budget_range,
            "category": category,
            "trends": ", ".join(trends[:4]),
            "point_forecast": point_forecast,
            "active_festival": active_festival,
            "languages": ", ".join(twin.languages),
            "target_language": target_lang,
        }

        generated = chain.invoke(payload)
    except Exception as exc:
        logger.warning("[campaign_generator] LLM offline/failed for %s (%s), using localized bilingual fallback", region_id, exc)
        vern_defaults = VERNACULAR_FALLBACKS.get(target_lang, VERNACULAR_FALLBACKS["Hindi"])

        generated = {
            "headline_en": f"{active_festival} Special: Trending {category.title()} Handpicked for {twin.city or twin.state}!",
            "body_en": f"Direct-from-maker prices starting at pocket-friendly rates for {segment_label}. Enjoy fast delivery & cash on delivery across {twin.state}.",
            "headline_vernacular": vern_defaults["headline"],
            "body_vernacular": vern_defaults["body"],
            "call_to_action_en": "Shop Festive Deals Now",
            "call_to_action_vernacular": vern_defaults["cta"],
            "key_selling_points": [
                f"Curated for {segment_label} ({budget_range})",
                f"Popular in {twin.city or twin.state} ({', '.join(trends[:2])})",
                "Verified direct seller pricing with free shipping",
            ],
            "target_channels": ["Instagram Reels", "WhatsApp Community Stores", "Regional In-App Banners"],
        }

    copy_lines = [
        generated.get("headline_en", "Special Regional Offer"),
        generated.get("body_en", "Exclusive deals available today."),
        f"[{target_lang}] " + generated.get("headline_vernacular", ""),
    ]

    logger.info("[campaign_generator] %s → Generated English + %s copy", region_id, target_lang)

    return {
        "campaign_result": generated,
        "campaign_copy": copy_lines,
        "campaign_en": {
            "headline": generated.get("headline_en"),
            "body": generated.get("body_en"),
            "cta": generated.get("call_to_action_en"),
        },
        "campaign_vernacular": {
            "language": target_lang,
            "headline": generated.get("headline_vernacular"),
            "body": generated.get("body_vernacular"),
            "cta": generated.get("call_to_action_vernacular"),
        },
        "explanation_log": [
            f"Campaign Studio ({region_id}): Generated bilingual copy in English & {target_lang} targeting {segment_label} for {active_festival}."
        ],
    }
