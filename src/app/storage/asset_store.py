import json
from pathlib import Path
from PIL import Image
from app.core.exceptions import AssetStorageError
from app.providers.base import ProviderImage
from app.utils.files import sha256_bytes
from app.utils.ids import new_id
class AssetStore:
    def __init__(self, root:str): self.root=Path(root)
    def save(self, session_id:str, turn_index:int, image:ProviderImage, metadata:dict):
        try:
            d=self.root/session_id/str(turn_index); d.mkdir(parents=True, exist_ok=True)
            aid=new_id('asset'); ext='png' if image.mime_type.endswith('png') else 'jpg'; path=d/f'{aid}.{ext}'
            path.write_bytes(image.data); width=height=None
            try:
                with Image.open(path) as im: width,height=im.size
            except Exception: pass
            meta={**metadata,'asset_id':aid,'sha256':sha256_bytes(image.data),'width':width,'height':height,'mime_type':image.mime_type,'path':str(path)}
            mpath=d/f'{aid}.json'; mpath.write_text(json.dumps(meta,indent=2,default=str))
            return aid,str(path),str(mpath),meta
        except Exception as exc: raise AssetStorageError(str(exc)) from exc
