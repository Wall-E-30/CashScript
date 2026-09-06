import os
import shutil
from PIL import Image
import pytesseract

# Configure Tesseract binary path if running on Windows and not in system PATH
if os.name == 'nt':
    custom_tess_path = os.getenv('TESSERACT_CMD')
    if custom_tess_path and os.path.exists(custom_tess_path):
        pytesseract.pytesseract.tesseract_cmd = custom_tess_path
    elif not shutil.which('tesseract'):
        standard_windows_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")
        ]
        for path in standard_windows_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                break

def extract_text_from_image(image_stream) -> str:
    """
    Takes an uploaded file stream (e.g. request.files['file'].stream),
    opens it using Pillow, passes it to pytesseract, and returns the raw extracted text string.
    """
    # Open image from stream
    image = Image.open(image_stream)

    # Convert non-RGB/L images (such as RGBA PNGs or CMYK) to RGB for OCR compatibility
    if image.mode not in ('L', 'RGB'):
        image = image.convert('RGB')

    # Run OCR via pytesseract
    raw_text = pytesseract.image_to_string(image)
    return raw_text
