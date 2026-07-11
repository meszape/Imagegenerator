import base64
from app.providers.gemini_adapter import GeminiImageAdapter
def test_parse_gemini():
    raw={'candidates':[{'finishReason':'STOP','content':{'parts':[{'inlineData':{'mimeType':'image/png','data':base64.b64encode(b'abc').decode()}}]}}]}
    r=GeminiImageAdapter(client=object())._parse(raw,{},None,'m')
    assert r.images[0].data==b'abc'
