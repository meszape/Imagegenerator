from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import get_settings
from app.core.enums import Provider, SafetyProfile
from app.core.exceptions import ProviderOutputParseError, ProviderRateLimitError, ProviderTemporaryError, ProviderAuthError, ProviderInvalidRequestError, ProviderSafetyBlockedError
from app.core.safety import openai_safety_capability_note
from app.providers.base import ImageProviderAdapter, ProviderCapabilities, ProviderImage, ProviderResult
from app.utils.files import decode_b64
class OpenAIImageAdapter(ImageProviderAdapter):
    provider=Provider.openai
    def __init__(self, client:Any|None=None):
        if client is None:
            from openai import OpenAI
            client=OpenAI(api_key=get_settings().openai_api_key, timeout=get_settings().request_timeout_seconds)
        self.client=client
    def _request_payload(self, model,prompt,previous_response_id,output_format,provider_config):
        payload={'model':model,'input':prompt,'tools':[{'type':'image_generation'}]}
        if previous_response_id: payload['previous_response_id']=previous_response_id
        if output_format: payload['tool_choice']={'type':'image_generation'}
        payload.update(provider_config or {})
        return payload
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1,max=8), retry=retry_if_exception_type(ProviderTemporaryError))
    def _call(self,payload):
        try: return self.client.responses.create(**payload)
        except Exception as exc: raise self.normalize_error(exc)
    def create_initial_image(self, model, prompt, safety_profile, custom_safety_settings=None, output_format=None, provider_config=None):
        payload=self._request_payload(model,prompt,None,output_format,provider_config); return self._parse(self._call(payload),payload,None,model)
    def continue_image_turn(self, model, prompt, previous_response_id, history, safety_profile, custom_safety_settings=None, output_format=None, provider_config=None):
        payload=self._request_payload(model,prompt,previous_response_id,output_format,provider_config); return self._parse(self._call(payload),payload,previous_response_id,model)
    def _dump(self,obj):
        if hasattr(obj,'model_dump'): return obj.model_dump(mode='json')
        if isinstance(obj,dict): return obj
        return getattr(obj,'__dict__',{'repr':repr(obj)})
    def _parse(self,response,payload,previous_response_id,model):
        raw=self._dump(response); output=raw.get('output') or getattr(response,'output',[]) or []
        images=[]; revised=None
        for item in output:
            d=self._dump(item); typ=d.get('type')
            if typ in {'image_generation_call','image_generation'} or 'result' in d:
                b64=d.get('result') or d.get('image') or d.get('b64_json')
                if b64:
                    revised=d.get('revised_prompt') or revised
                    images.append(ProviderImage(decode_b64(b64),'image/png',{'image_generation_call_id':d.get('id')},d.get('revised_prompt')))
        if not images: raise ProviderOutputParseError('OpenAI response did not contain image output', provider='openai', details={'response':raw})
        return ProviderResult(Provider.openai,model,payload,raw,raw.get('id'),previous_response_id,images,revised_prompt=revised)
    def normalize_error(self, exc):
        name=exc.__class__.__name__.lower(); msg=str(exc)
        if 'auth' in name or 'authentication' in msg.lower(): return ProviderAuthError(msg,'openai')
        if 'rate' in name or '429' in msg: return ProviderRateLimitError(msg,'openai')
        if 'safety' in msg.lower() or 'policy' in msg.lower(): return ProviderSafetyBlockedError(msg,'openai')
        if 'badrequest' in name or 'invalid' in name: return ProviderInvalidRequestError(msg,'openai')
        return ProviderTemporaryError(msg,'openai')
    def get_capabilities(self): return ProviderCapabilities(Provider.openai,True,True,False,False,False,True,[openai_safety_capability_note(),'Uses Responses API image_generation tool; previous_response_id continues turns.'])
