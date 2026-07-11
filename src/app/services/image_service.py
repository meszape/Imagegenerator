import time
from app.config import get_settings
from app.core.enums import Provider, SafetyProfile
from app.core.exceptions import AppError
from app.core.models import TurnModel, AssetModel
from app.core.provider_router import ProviderRouter
from app.core.schemas import GenerateRequest
from app.logging import get_logger
from app.storage.asset_store import AssetStore
from app.storage.repositories import Repository
from app.utils.ids import new_id
log=get_logger(__name__)
def normalize_instruction(prompt:str)->str: return ' '.join(prompt.strip().split())
class ImageService:
    def __init__(self, repo:Repository, router:ProviderRouter, asset_store:AssetStore|None=None): self.repo=repo; self.router=router; self.asset_store=asset_store or AssetStore(get_settings().asset_root)
    def generate(self, session_id:str, req:GenerateRequest):
        sess=self.repo.get_session(session_id); safety=req.safety_profile or SafetyProfile(sess.default_safety_profile); idx=self.repo.next_turn_index(session_id); history=[t.__dict__ for t in self.repo.list_turns(session_id)]; prev=self.repo.last_provider_response_id(session_id,Provider(sess.provider)); fallback_attempted=False; original_error=None; start=time.perf_counter()
        try: result=self._call(Provider(sess.provider),sess.model,req,idx,history,prev,safety,sess.provider_config)
        except AppError as exc:
            if not self.router.can_fallback(exc,req.fallback_provider): raise
            fallback_attempted=True; original_error={'code':exc.code,'message':exc.message,'provider':exc.provider}; result=self._call(req.fallback_provider,sess.model,req,idx,history,None,safety,{})
        turn=TurnModel(turn_id=new_id('turn'),session_id=session_id,turn_index=idx,user_prompt=req.prompt,normalized_instruction=normalize_instruction(req.prompt),provider_request_payload=result.request_payload,provider_response_payload=result.raw_response,provider_response_id=result.response_id,previous_provider_response_id=result.previous_response_id,safety_profile_used=safety.value,block_status='none',block_reason=None,revised_prompt=result.revised_prompt,output_assets=[])
        self.repo.add_turn(turn); assets=[]
        for img in result.images:
            aid,path,mpath,meta=self.asset_store.save(session_id,idx,img,{'provider':result.provider.value,'model':result.model,'prompt_info':{'user_prompt':req.prompt,'metadata':req.metadata},'provider_ids':img.provider_ids})
            a=self.repo.add_asset(AssetModel(asset_id=aid,session_id=session_id,turn_id=turn.turn_id,turn_index=idx,path=path,metadata_path=mpath,sha256=meta['sha256'],width=meta['width'],height=meta['height'],mime_type=meta['mime_type'],provider=result.provider.value,model=result.model,provider_ids=img.provider_ids,prompt_info={'user_prompt':req.prompt,'metadata':req.metadata}))
            assets.append(a)
        turn.output_assets=[a.asset_id for a in assets]; self.repo.db.commit(); self.repo.db.refresh(turn)
        log.info('image_turn_complete', extra={'session_id':session_id,'turn_id':turn.turn_id,'provider':result.provider.value,'model':result.model,'safety_profile':safety.value,'latency_ms':round((time.perf_counter()-start)*1000),'result_status':'ok'})
        return turn,assets,result.provider.value,fallback_attempted,original_error
    def _call(self,provider,model,req,idx,history,prev,safety,provider_config):
        adapter=self.router.get(provider)
        return adapter.create_initial_image(model,req.prompt,safety,req.custom_safety_settings,req.output_format,provider_config) if idx==1 else adapter.continue_image_turn(model,req.prompt,prev,history,safety,req.custom_safety_settings,req.output_format,provider_config)
