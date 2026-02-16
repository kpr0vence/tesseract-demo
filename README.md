# tesseract-demo
small working demo of tesseract reading the characters on a receipt and its black and white variant

## Run as an HTTP service (FastAPI)

Install dependencies (Poetry):

```bash
poetry install
```

Start the server:

```bash
poetry run uvicorn main:app --reload
```

OCR an image via multipart form upload:

```bash
curl -s \
  -F "file=@bnwReceipt.png" \
  http://127.0.0.1:8000/ocr | python -m json.tool
```

This will also write an annotated image (red boxes) to disk and return an `annotated_image_url`.

Health check:

```bash
curl -s http://127.0.0.1:8000/health
```

## Notes

- This project uses `pytesseract`, which requires the **Tesseract** binary to be installed and on your PATH.
- FastAPI file uploads require `python-multipart` (included in `pyproject.toml`).
- Annotated images are written to `static/annotated/` and served at `/static/annotated/<uuid>.png`.

## Improving accuracy (especially prices)

If your bounding boxes / OCR misses the **price column** on the far right, it’s usually because the digits are **low-contrast** and **small/thin**.

- **Preprocess before OCR (biggest win)**:
  - Convert to grayscale
  - Boost contrast (e.g. autocontrast)
  - Upscale 2–4×
  - Binarize / adaptive threshold (OpenCV is great for this)
- **OCR the prices as a separate ROI (second biggest win)**:
  - Crop the right-most ~25–35% of the receipt and run a second OCR pass on that crop
  - Merge results back by adding the crop’s x-offset to the returned bounding boxes
- **Use a numeric-focused config for the prices ROI**:
  - Try `--psm 6` (also test `--psm 4` and `--psm 11`)
  - Use a whitelist: `-c tessedit_char_whitelist=0123456789.$,`
  - Enable numeric mode: `-c classify_bln_numeric_mode=1`
- **Crop out scribbles/headers when possible**:
  - Large dark marks (like marker scribbles) can confuse page segmentation; cropping the receipt body can help.
