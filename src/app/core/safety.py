from app.core.enums import SafetyProfile
GEMINI_CATEGORIES=['HARM_CATEGORY_HARASSMENT','HARM_CATEGORY_HATE_SPEECH','HARM_CATEGORY_SEXUALLY_EXPLICIT','HARM_CATEGORY_DANGEROUS_CONTENT','HARM_CATEGORY_CIVIC_INTEGRITY']
GEMINI_THRESHOLDS={'OFF','BLOCK_NONE','BLOCK_ONLY_HIGH','BLOCK_MEDIUM_AND_ABOVE','BLOCK_LOW_AND_ABOVE','HARM_BLOCK_THRESHOLD_UNSPECIFIED'}
PROFILE_TO_GEMINI={SafetyProfile.strict:'BLOCK_LOW_AND_ABOVE',SafetyProfile.balanced:'BLOCK_MEDIUM_AND_ABOVE',SafetyProfile.permissive:'BLOCK_ONLY_HIGH'}
def map_gemini_safety(profile:SafetyProfile, overrides:dict[str,str]|None=None)->list[dict[str,str]]:
    if profile==SafetyProfile.custom and not overrides: raise ValueError('custom safety requires overrides')
    threshold=PROFILE_TO_GEMINI.get(profile,'BLOCK_MEDIUM_AND_ABOVE')
    settings={c:threshold for c in GEMINI_CATEGORIES}
    for c,t in (overrides or {}).items():
        if c not in GEMINI_CATEGORIES: raise ValueError(f'unsupported Gemini safety category: {c}')
        if t not in GEMINI_THRESHOLDS: raise ValueError(f'unsupported Gemini safety threshold: {t}')
        settings[c]=t
    return [{'category':c,'threshold':t} for c,t in settings.items()]
def openai_safety_capability_note()->str:
    return 'OpenAI Responses image_generation safety controls are provider/model enforced; this service does not expose invented safety-disabling flags.'
