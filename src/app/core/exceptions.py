class AppError(Exception):
    code='app_error'; status_code=500
    def __init__(self,message:str,provider:str|None=None,details:dict|None=None): super().__init__(message); self.message=message; self.provider=provider; self.details=details or {}
class ProviderAuthError(AppError): code='provider_auth_error'; status_code=401
class ProviderRateLimitError(AppError): code='provider_rate_limit'; status_code=429
class ProviderSafetyBlockedError(AppError): code='provider_safety_blocked'; status_code=422
class ProviderTemporaryError(AppError): code='provider_temporary_error'; status_code=503
class ProviderInvalidRequestError(AppError): code='provider_invalid_request'; status_code=400
class ProviderOutputParseError(AppError): code='provider_output_parse_error'; status_code=502
class AssetStorageError(AppError): code='asset_storage_error'; status_code=500
class SessionNotFoundError(AppError): code='session_not_found'; status_code=404
class AssetNotFoundError(AppError): code='asset_not_found'; status_code=404
