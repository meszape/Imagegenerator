import base64
from typing import Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import get_settings
from app.core.enums import Provider, SafetyProfile
from app.core.exceptions import ProviderOutputParseError, ProviderRateLimitError, ProviderTemporaryError, ProviderAuthError, ProviderInvalidRequestError, ProviderSafetyBlockedError
from app.core.safety import map_gemini_safety
from app.providers.base import ImageProviderAdapter, ProviderCapabilities, ProviderImage, ProviderResult
class GeminiImageAdapter(ImageProviderAdapter):
    provider=Provider.gemini
    def __init__(self, client:Any|None=None):
        if client is None:
            from google import genai
            client=genai.Client(api_key=get_settings().gemini_api_key)
        self.client=client
    def _build_contents(self,prompt,history):
        prefix=''
        if history:
            recent=history[-get_settings().max_turn_context:]
            prefix='Prior turns summary:\n'+'\n'.join(f"{h.get('turn_index')}: {h.get('normalized_instruction')}" for h in recent)+'\nNext edit instruction:\n'
        return prefix+prompt
    def _payload(self,model,prompt,safety_profile,custom,output_format,history=None):
        # Internal profiles are service-level convenience names; Gemini thresholds remain provider/model enforced per request.
        return {'model':model,'contents':self._build_contents(prompt,history or []),'config':{'response_modalities':['IMAGE','TEXT'],'safety_settings':map_gemini_safety(safety_profile, custom)}}
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1,max=8), retry=retry_if_exception_type(ProviderTemporaryError))
    def _call(self,payload):
        try: return self.client.models.generate_content(**payload)
        except Exception as exc: raise self.normalize_error(exc)
    def create_initial_image(self, model, prompt, safety_profile, custom_safety_settings=None, output_format=None, provider_config=None):
        payload=self._payload(model,prompt,safety_profile,custom_safety_settings,output_format); payload.update(provider_config or {})
        return self._parse(self._call(payload),payload,None,model)
    def continue_image_turn(self, model, prompt, previous_response_id, history, safety_profile, custom_safety_settings=None, output_format=None, provider_config=None):
        payload=self._payload(model,prompt,safety_profile,custom_safety_settings,output_format,history); payload.update(provider_config or {})
        return self._parse(self._call(payload),payload,previous_response_id,model)
    def _dump(self,obj):
        if hasattr(obj,'model_dump'): return obj.model_dump(mode='json')
        if isinstance(obj,dict): return obj
        return getattr(obj,'__dict__',{'repr':repr(obj)})
    def _parse(self,response,payload,previous_response_id,model):
        raw=self._dump(response); images=[]; feedback={'prompt_feedback':raw.get('prompt_feedback') or raw.get('promptFeedback'), 'candidates':[]}
        if feedback['prompt_feedback'] and feedback['prompt_feedback'].get('block_reason'): raise ProviderSafetyBlockedError('Gemini prompt blocked','gemini',feedback)
        for cand in raw.get('candidates',[]) or []:
            feedback['candidates'].append({'finish_reason':cand.get('finish_reason') or cand.get('finishReason'),'safety_ratings':cand.get('safety_ratings') or cand.get('safetyRatings')})
            if (cand.get('finish_reason') or cand.get('finishReason'))=='SAFETY': raise ProviderSafetyBlockedError('Gemini candidate blocked','gemini',feedback)
            parts=((cand.get('content') or {}).get('parts') or [])
            for part in parts:
                inline=part.get('inline_data') or part.get('inlineData')
                if inline and inline.get('data'):
                    data=inline['data']; images.append(ProviderImage(base64.b64decode(data) if isinstance(data,str) else data, inline.get('mime_type') or inline.get('mimeType') or 'image/png'))
        if not images: raise ProviderOutputParseError('Gemini response did not contain image output','gemini',{'response':raw})
        return ProviderResult(Provider.gemini,model,payload,raw,raw.get('response_id') or raw.get('responseId'),previous_response_id,images,feedback)
    def normalize_error(self, exc):
        msg=str(exc); low=msg.lower()
        if 'api key' in low or 'auth' in low: return ProviderAuthError(msg,'gemini')
        if 'quota' in low or '429' in msg: return ProviderRateLimitError(msg,'gemini')
        if 'safety' in low or 'blocked' in low: return ProviderSafetyBlockedError(msg,'gemini')
        if 'invalid' in low or '400' in msg: return ProviderInvalidRequestError(msg,'gemini')
        return ProviderTemporaryError(msg,'gemini')
    def get_capabilities(self): return ProviderCapabilities(Provider.gemini,True,False,True,True,True,False,['Uses Google GenAI SDK generate_content with per-request safety_settings. Multi-turn is bounded context replay.'])
