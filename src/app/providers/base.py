from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from app.core.enums import Provider, SafetyProfile
@dataclass
class ProviderImage: data:bytes; mime_type:str='image/png'; provider_ids:dict[str,Any]=field(default_factory=dict); revised_prompt:str|None=None
@dataclass
class ProviderResult:
    provider:Provider; model:str; request_payload:dict[str,Any]; raw_response:dict[str,Any]; response_id:str|None; previous_response_id:str|None; images:list[ProviderImage]; safety_feedback:dict[str,Any]=field(default_factory=dict); revised_prompt:str|None=None
@dataclass
class ProviderCapabilities:
    provider:Provider; supports_multi_turn:bool; supports_previous_response_id:bool; supports_per_category_safety:bool; supports_block_none:bool; supports_off:bool; supports_revised_prompt:bool; notes:list[str]
class ImageProviderAdapter(ABC):
    provider:Provider
    @abstractmethod
    def create_initial_image(self, model:str, prompt:str, safety_profile:SafetyProfile, custom_safety_settings:dict[str,str]|None=None, output_format:str|None=None, provider_config:dict[str,Any]|None=None)->ProviderResult: ...
    @abstractmethod
    def continue_image_turn(self, model:str, prompt:str, previous_response_id:str|None, history:list[dict[str,Any]], safety_profile:SafetyProfile, custom_safety_settings:dict[str,str]|None=None, output_format:str|None=None, provider_config:dict[str,Any]|None=None)->ProviderResult: ...
    @abstractmethod
    def get_capabilities(self)->ProviderCapabilities: ...
    def validate_config(self, config:dict[str,Any]|None)->None: return None
    def normalize_error(self, exc:Exception): return exc
