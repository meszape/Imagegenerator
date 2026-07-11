import base64
from app.providers.openai_adapter import OpenAIImageAdapter
class Resp:
    def model_dump(self,mode='json'):
        return {'id':'resp_1','output':[{'type':'image_generation_call','id':'call_1','result':base64.b64encode(b'abc').decode(),'revised_prompt':'cat'}]}
def test_parse_openai():
    r=OpenAIImageAdapter(client=object())._parse(Resp(),{},None,'m')
    assert r.response_id=='resp_1' and r.images[0].data==b'abc' and r.revised_prompt=='cat'
