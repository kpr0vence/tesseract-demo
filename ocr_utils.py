import statistics
from typing import Any
import pytesseract
from PIL import Image, ImageDraw
from pytesseract import Output

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

TESS_CONFIG = "--oem 3 --psm 4"  # fast OCR config

def ocr_image(image: Image.Image, *, lowercase_lines: bool = True) -> dict[str, Any]:
    """
    OCR an image with Tesseract and return:
      - full `text`
      - `lines` (optionally lowercased)
      - `mean_confidence`
      - `words`: word-level text, confidence, and bounding boxes
    Always returns safe defaults even if Tesseract fails.
    """
    try:
        text = pytesseract.image_to_string(image, config=TESS_CONFIG)
    except Exception as e:
        print("[ocr] image_to_string failed:", e)
        text = ""

    # line splitting
    try:
        lines = text.splitlines()
        lines = [line.strip() for line in lines if isinstance(line, str) and line.strip()]
        if lowercase_lines:
            lines = [line.lower() for line in lines]
    except Exception as e:
        print("[ocr] line splitting failed:", e)
        lines = []

    # word-level data
    words: list[dict[str, Any]] = []
    confs: list[float] = []

    try:
        data = pytesseract.image_to_data(image, output_type=Output.DICT, config=TESS_CONFIG)
        n = len(data.get("text", []))
        for i in range(n):
            w = (data["text"][i] or "").strip()
            if not w:
                continue
            try:
                conf = float(data["conf"][i])
            except (TypeError, ValueError):
                conf = -1.0
            if conf >= 0:
                confs.append(conf)
            words.append(
                {
                    "text": w,
                    "conf": conf,
                    "bbox": {
                        "left": int(data["left"][i]),
                        "top": int(data["top"][i]),
                        "width": int(data["width"][i]),
                        "height": int(data["height"][i]),
                    },
                }
            )
    except Exception as e:
        print("[ocr] image_to_data failed:", e)
        words = []
        confs = []

    mean_conf = statistics.fmean(confs) if confs else None

    return {
        "text": text or "",
        "lines": lines,
        "mean_confidence": mean_conf,
        "words": words,
    }
