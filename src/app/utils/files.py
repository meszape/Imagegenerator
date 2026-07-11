import base64, hashlib
def decode_b64(data:str)->bytes:
    return base64.b64decode(data.split(',',1)[-1])
def sha256_bytes(data:bytes)->str: return hashlib.sha256(data).hexdigest()
