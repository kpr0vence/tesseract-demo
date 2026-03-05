import statistics
from typing import Any

import pytesseract
from PIL import Image, ImageDraw
from pytesseract import Output

TESS_CONFIG = "--oem 3 --psm 4" # improves tesseract speed


def ocr_image(image: Image.Image, *, lowercase_lines: bool = True) -> dict[str, Any]:
    """
    OCR an image with Tesseract and return:
      - full `text`
      - `lines` (optionally lowercased)
      - `mean_confidence` (mean of non-negative word confidences)
      - `words`: word-level text, confidence, and bounding boxes

    Notes:
    - Tesseract confidences are per-word, typically 0-100; sometimes "-1" for non-words.
    """
    text = pytesseract.image_to_string(image, config=TESS_CONFIG)

    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]

    if lowercase_lines:
        lines = [line.lower() for line in lines]

    # Get word-level data
    data = pytesseract.image_to_data(
        image,
        output_type=Output.DICT,
        config=TESS_CONFIG,
    )

    words: list[dict[str, Any]] = []
    confs: list[float] = []

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

    mean_conf = statistics.fmean(confs) if confs else None

    return {
        "text": text,
        "lines": lines,
        "mean_confidence": mean_conf,
        "words": words,
    }
