import statistics
from typing import Any

import pytesseract
from PIL import Image, ImageDraw
from pytesseract import Output


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
    text = pytesseract.image_to_string(image)

    lines = text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    if lowercase_lines:
        lines = [line.lower() for line in lines]

    data = pytesseract.image_to_data(image, output_type=Output.DICT)
    words: list[dict[str, Any]] = []
    confs: list[float] = []
    n = len(data.get("text", []))

    for i in range(n):
        w = (data["text"][i] or "").strip()
        if not w:
            continue

        raw_conf = data["conf"][i]
        try:
            conf = float(raw_conf)
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


def draw_word_boxes(
    image: Image.Image,
    words: list[dict[str, Any]],
    *,
    outline: str = "red",
    width: int = 2,
) -> Image.Image:
    """
    Return a NEW image with rectangles drawn for each word bbox.

    Expects `words` items shaped like the output from `ocr_image()`:
      {"text": str, "conf": float, "bbox": {"left": int, "top": int, "width": int, "height": int}}
    """
    # Ensure we can draw colored outlines even if the source is grayscale.
    out = image.convert("RGB").copy()
    draw = ImageDraw.Draw(out)

    for w in words:
        bbox = (w or {}).get("bbox") or {}
        left = int(bbox.get("left", 0))
        top = int(bbox.get("top", 0))
        bw = int(bbox.get("width", 0))
        bh = int(bbox.get("height", 0))
        if bw <= 0 or bh <= 0:
            continue

        right = left + bw
        bottom = top + bh
        draw.rectangle([left, top, right, bottom], outline=outline, width=width)

    return out

