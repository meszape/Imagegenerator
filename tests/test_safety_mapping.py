import pytest
from app.core.enums import SafetyProfile
from app.core.safety import map_gemini_safety

def test_gemini_balanced_mapping():
    s=map_gemini_safety(SafetyProfile.balanced)
    assert all(x['threshold']=='BLOCK_MEDIUM_AND_ABOVE' for x in s)

def test_gemini_custom_override():
    s=map_gemini_safety(SafetyProfile.custom, {'HARM_CATEGORY_HATE_SPEECH':'BLOCK_NONE'})
    assert any(x['category']=='HARM_CATEGORY_HATE_SPEECH' and x['threshold']=='BLOCK_NONE' for x in s)

def test_bad_threshold():
    with pytest.raises(ValueError): map_gemini_safety(SafetyProfile.custom, {'HARM_CATEGORY_HATE_SPEECH':'NOPE'})
