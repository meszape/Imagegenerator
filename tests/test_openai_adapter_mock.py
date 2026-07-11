import base64
from app.core.enums import SafetyProfile
from app.providers.openai_adapter import OpenAIImageAdapter


class Resp:
    def model_dump(self, mode='json'):
        return {'id': 'resp_1', 'output': [{'type': 'image_generation_call', 'id': 'call_1', 'result': base64.b64encode(b'abc').decode(), 'revised_prompt': 'cat'}]}


def test_parse_openai():
    r = OpenAIImageAdapter(client=object())._parse(Resp(), {}, None, 'm')
    assert r.response_id == 'resp_1' and r.images[0].data == b'abc' and r.revised_prompt == 'cat'


def test_request_payload_includes_low_moderation_for_permissive():
    payload = OpenAIImageAdapter(client=object())._request_payload('gpt-image-1.5', 'cat', None, 'png', {}, SafetyProfile.permissive)
    assert payload['tools'][0]['moderation'] == 'low'


def test_request_payload_includes_auto_moderation_for_strict_and_balanced():
    adapter = OpenAIImageAdapter(client=object())
    strict = adapter._request_payload('gpt-image-1.5', 'cat', None, None, {}, SafetyProfile.strict)
    balanced = adapter._request_payload('gpt-image-1.5', 'cat', None, None, {}, SafetyProfile.balanced)
    assert strict['tools'][0]['moderation'] == 'auto'
    assert balanced['tools'][0]['moderation'] == 'auto'


def test_request_payload_threads_image_generation_tool_overrides():
    payload = OpenAIImageAdapter(client=object())._request_payload(
        'gpt-image-1.5', 'cat', None, None,
        {'quality': 'high', 'size': '1024x1024', 'background': 'transparent', 'action': 'generate', 'input_fidelity': 'high', 'partial_images': 2, 'moderation': 'auto'},
        SafetyProfile.permissive,
    )
    tool = payload['tools'][0]
    assert tool['moderation'] == 'auto'
    assert tool['quality'] == 'high'
    assert tool['size'] == '1024x1024'
    assert tool['background'] == 'transparent'
    assert tool['action'] == 'generate'
    assert tool['input_fidelity'] == 'high'
    assert tool['partial_images'] == 2
