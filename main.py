from __future__ import annotations

import uuid
from io import BytesIO
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, HTTPException, Request, UploadFile
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from ocr_utils import draw_word_boxes, ocr_image

app = FastAPI(title="tesseract-demo", version="0.1.0")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
ANNOTATED_DIR = STATIC_DIR / "annotated"
ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ocr")
async def ocr_endpoint(request: Request, file: UploadFile = File(...)) -> dict[str, Any]:
    """
    Accepts multipart/form-data:
      - file: uploaded image
    Returns JSON with text, lines, mean_confidence, and word-level boxes/conf.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=415, detail="file must be an image upload")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty upload")

    try:
        img = Image.open(BytesIO(raw))
        img.load()
    except UnidentifiedImageError:
        raise HTTPException(status_code=415, detail="unsupported/invalid image")

    try:
        result = ocr_image(img)
        annotated = draw_word_boxes(img, result["words"])
        filename = f"{uuid.uuid4().hex}.png"
        out_path = ANNOTATED_DIR / filename
        annotated.save(out_path, format="PNG")

        url_path = f"/static/annotated/{filename}"
        result["annotated_image_url"] = str(request.base_url).rstrip("/") + url_path
        return result
    except Exception as e:  # pragma: no cover
        # Common case here is "tesseract is not installed or it's not in your PATH".
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

