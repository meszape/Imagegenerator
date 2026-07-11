import base64
from app.core.enums import SafetyProfile
from app.core.safety import GEMINI_CATEGORIES
from app.providers.gemini_adapter import GeminiImageAdapter


def test_parse_gemini():
    raw = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(b'abc').decode()}}]}}]}
    r = GeminiImageAdapter(client=object())._parse(raw, {}, None, 'm')
    assert r.images[0].data == b'abc'


def test_payload_permissive_uses_block_none_for_all_categories():
    payload = GeminiImageAdapter(client=object())._payload('gemini-3.1-flash-image', 'cat', SafetyProfile.permissive, None, None)
    settings = payload['config']['safety_settings']
    assert {s['category'] for s in settings} == set(GEMINI_CATEGORIES)
    assert all(s['threshold'] == 'BLOCK_NONE' for s in settings)


def test_payload_custom_off_override_respects_other_categories():
    payload = GeminiImageAdapter(client=object())._payload(
        'gemini-3.1-flash-image', 'cat', SafetyProfile.permissive,
        {'HARM_CATEGORY_DANGEROUS_CONTENT': 'OFF'}, None,
    )
    settings = {s['category']: s['threshold'] for s in payload['config']['safety_settings']}
    assert settings['HARM_CATEGORY_DANGEROUS_CONTENT'] == 'OFF'
    for category, threshold in settings.items():
        if category != 'HARM_CATEGORY_DANGEROUS_CONTENT':
            assert threshold == 'BLOCK_NONE'
