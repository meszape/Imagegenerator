from app.core.enums import SafetyProfile

GEMINI_CATEGORIES = [
    'HARM_CATEGORY_HARASSMENT',
    'HARM_CATEGORY_HATE_SPEECH',
    'HARM_CATEGORY_SEXUALLY_EXPLICIT',
    'HARM_CATEGORY_DANGEROUS_CONTENT',
    'HARM_CATEGORY_CIVIC_INTEGRITY',
]
GEMINI_THRESHOLDS = {
    'OFF',
    'BLOCK_NONE',
    'BLOCK_ONLY_HIGH',
    'BLOCK_MEDIUM_AND_ABOVE',
    'BLOCK_LOW_AND_ABOVE',
    'HARM_BLOCK_THRESHOLD_UNSPECIFIED',
}
PROFILE_TO_GEMINI = {
    SafetyProfile.strict: 'BLOCK_LOW_AND_ABOVE',
    SafetyProfile.balanced: 'BLOCK_MEDIUM_AND_ABOVE',
    # BLOCK_NONE is the documented permissive default used here because it
    # still returns safety ratings while avoiding configurable-category
    # blocking. OFF remains available via custom_safety_settings per category
    # for callers that explicitly want to disable that adjustable filter.
    # Provider-enforced core-harm protections can still apply either way.
    SafetyProfile.permissive: 'BLOCK_NONE',
}
OPENAI_MODERATION_VALUES = {'auto', 'low'}
PROFILE_TO_OPENAI_MODERATION = {
    SafetyProfile.strict: 'auto',
    SafetyProfile.balanced: 'auto',
    SafetyProfile.permissive: 'low',
    SafetyProfile.custom: 'low',
}

def map_gemini_safety(profile: SafetyProfile, overrides: dict[str, str] | None = None) -> list[dict[str, str]]:
    if profile == SafetyProfile.custom and not overrides:
        raise ValueError('custom safety requires overrides')
    threshold = PROFILE_TO_GEMINI.get(profile, 'BLOCK_MEDIUM_AND_ABOVE')
    settings = {c: threshold for c in GEMINI_CATEGORIES}
    for c, t in (overrides or {}).items():
        if c not in GEMINI_CATEGORIES:
            raise ValueError(f'unsupported Gemini safety category: {c}')
        if t not in GEMINI_THRESHOLDS:
            raise ValueError(f'unsupported Gemini safety threshold: {t}')
        settings[c] = t
    return [{'category': c, 'threshold': t} for c, t in settings.items()]

def map_openai_safety(profile: SafetyProfile, moderation_override: str | None = None) -> str:
    moderation = moderation_override or PROFILE_TO_OPENAI_MODERATION.get(profile, 'auto')
    if moderation not in OPENAI_MODERATION_VALUES:
        raise ValueError(f'unsupported OpenAI moderation value: {moderation}')
    return moderation

def openai_safety_capability_note() -> str:
    return 'OpenAI Responses image_generation uses the documented moderation parameter (auto/low); this service does not expose invented safety-disabling flags.'
