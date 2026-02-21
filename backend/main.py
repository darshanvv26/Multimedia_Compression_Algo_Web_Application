from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from algorithms import static_huffman, dynamic_huffman, arithmetic, lzw

app = FastAPI(title="Compression API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompressRequest(BaseModel):
    algorithm: str   # "static_huffman" | "dynamic_huffman" | "arithmetic" | "lzw"
    text: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/compress")
def compress(req: CompressRequest):
    algo = req.algorithm.lower().strip()
    text = req.text

    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Input too long. Maximum 5000 characters.")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    try:
        if algo == "static_huffman":
            return static_huffman.compress(text)
        elif algo == "dynamic_huffman":
            return dynamic_huffman.compress(text)
        elif algo == "arithmetic":
            return arithmetic.compress(text)
        elif algo == "lzw":
            return lzw.compress(text)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown algorithm: {algo}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
