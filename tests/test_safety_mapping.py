import pytest
from app.core.enums import SafetyProfile
from app.core.safety import map_gemini_safety, map_openai_safety


def test_gemini_balanced_mapping():
    s = map_gemini_safety(SafetyProfile.balanced)
    assert all(x['threshold'] == 'BLOCK_MEDIUM_AND_ABOVE' for x in s)


def test_gemini_permissive_maps_to_block_none():
    s = map_gemini_safety(SafetyProfile.permissive)
    assert all(x['threshold'] == 'BLOCK_NONE' for x in s)
    assert not any(x['threshold'] == 'BLOCK_ONLY_HIGH' for x in s)


def test_openai_permissive_maps_to_low_moderation():
    assert map_openai_safety(SafetyProfile.permissive) == 'low'
    assert map_openai_safety(SafetyProfile.custom) == 'low'
    assert map_openai_safety(SafetyProfile.strict) == 'auto'
    assert map_openai_safety(SafetyProfile.balanced) == 'auto'


def test_gemini_custom_override():
    s = map_gemini_safety(SafetyProfile.custom, {'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE'})
    assert any(x['category'] == 'HARM_CATEGORY_HATE_SPEECH' and x['threshold'] == 'BLOCK_NONE' for x in s)


def test_bad_threshold():
    with pytest.raises(ValueError):
        map_gemini_safety(SafetyProfile.custom, {'HARM_CATEGORY_HATE_SPEECH': 'NOPE'})
