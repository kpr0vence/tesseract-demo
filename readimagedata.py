import pytesseract
from pytesseract import Output
from PIL import Image

print("---TO ONE WHOLE STRING---")
img=Image.open("bnwReceipt.png")    # open the image
tes=pytesseract.image_to_string(img)    # OCRs takes in an image object
# print(tes)

lines = tes.splitlines()
lines = [line.lower() for line in lines if line.strip()]
for line in lines:
    print(line)

# The only problem is I don't have any confidence scores here. not sure if I need them?