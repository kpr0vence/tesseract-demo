from fastapi import FastAPI, File, HTTPException, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from pillow_heif import register_heif_opener, read_heif
from io import BytesIO

from ocr_utils import ocr_image

app = FastAPI(title="tesseract-demo", version="0.1.0")
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
ANNOTATED_DIR = STATIC_DIR / "annotated"
ANNOTATED_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/health")
def health():
    return {"status": "ok"}

register_heif_opener()      # All I need to do should just be to register 
# the opener so the rest of the code can just work as normal

@app.post("/ocr")
async def ocr_endpoint(request: Request, file: UploadFile = File(...)):
    print(file.filename)
    if (not file.content_type or not file.content_type.startswith("image/") and not ('heic' in file.filename.lower())):
        # if ('heic' in file.filename.lower()):
        #     print("HEIC DETECTED")
        #     heif_file = read_heif(file.filename)
        #     image = Image.frombytes(
        #         heif_file.mode,
        #         heif_file.size,
        #         heif_file.data,
        #         "raw",
        #     )

        #     image.save("./picture_name.png", format("png"))
        #     print(image)


        raise HTTPException(status_code=415, detail="file must be an image upload")
    
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="empty upload")

    try:
        img = Image.open(BytesIO(raw))
        if ('heic' in file.filename.lower()):
            print("HEIC DETECTED")
            heif_file = read_heif(file.filename)
            img = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
            )

            img.save("./picture_name.png", format("png"))
        img.load()
    except UnidentifiedImageError:
        raise HTTPException(status_code=415, detail="unsupported/invalid image")
    except Exception as e:
        print("[ocr] failed to open image:", e)
        raise HTTPException(status_code=500, detail=f"failed to open image: {e}")
     

    try:
        result = ocr_image(img)
        print("[ocr] OCR success, first 100 chars:", result["text"][:100])
        return result
    except Exception as e:
        print("[ocr] OCR failed:", e)
        # return safe defaults instead of 500
        return {
            "text": "",
            "lines": [],
            "mean_confidence": None,
            "words": [],
            "error": str(e),
        }