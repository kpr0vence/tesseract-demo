import cv2
import numpy as np
from PIL import Image


def preprocess_for_ocr(pil_img: Image.Image) -> Image.Image:
    img = np.array(pil_img) # Convert it to something OpenCV can use

    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)    # grayscale

    if max(gray.shape) < 1000:  # upscale
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    

    return Image.fromarray(gray)


# Use PIL to convert any image format to any other image
# Might be a good idea to still limit the file formats (on Mr. Fridge)
'''
Install pillow-heif
Real easy process just
'''