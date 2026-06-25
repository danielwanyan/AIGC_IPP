import os
os.environ["HEADROOM_DISABLE_PROTECTION"] = "1"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from headroom.transforms.kompress_compressor import KompressCompressor

app = FastAPI(title="Headroom Compression Service")

_compressor = None

def get_compressor():
    global _compressor
    if _compressor is None:
        _compressor = KompressCompressor()
    return _compressor

class CompressRequest(BaseModel):
    text: str
    target_ratio: float = 0.5

class CompressResponse(BaseModel):
    compressed: str
    original_tokens: int
    compressed_tokens: int
    tokens_saved: int
    compression_ratio: float

@app.post("/compress", response_model=CompressResponse)
async def compress(request: CompressRequest):
    try:
        compressor = get_compressor()
        result = compressor.compress(request.text, target_ratio=request.target_ratio)
        return CompressResponse(
            compressed=result.compressed,
            original_tokens=result.original_tokens,
            compressed_tokens=result.compressed_tokens,
            tokens_saved=result.tokens_saved,
            compression_ratio=round(1 - result.compression_ratio, 4),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8787)
