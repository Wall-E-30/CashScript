import os
import re
import shutil
from datetime import datetime
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


def _clean_number(val_str: str) -> float | None:
    """Helper to sanitize number string and return float if plausible amount."""
    cleaned = val_str.replace(',', '').strip()
    try:
        val = float(cleaned)
        # Avoid phone numbers or absurd invoice numbers (> 10,000,000)
        if 0 < val < 10000000:
            return round(val, 2)
    except ValueError:
        pass
    return None


def extract_amount(text: str) -> float | None:
    """
    Scans OCR text for keywords like TOTAL, NET, AMOUNT, RS, INR, or ₹,
    identifies numerical currency values (e.g. 1,278.00 or 1278.00),
    and selects the most probable final total amount.
    """
    if not text:
        return None

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # High priority keywords (unambiguous bill totals)
    high_priority_re = re.compile(
        r'\b(grand\s*total|net\s*payable|total\s*payable|amount\s*payable|total\s*amount|balance\s*due|final\s*total)\b',
        re.IGNORECASE
    )
    
    # Medium priority keywords
    medium_priority_re = re.compile(r'\b(total|net|amount|payable|due)\b', re.IGNORECASE)

    # Explicit currency symbols/prefixes
    currency_re = re.compile(
        r'(?:(?:RS|INR|₹|\$)\.?\s*)([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+(?:\.[0-9]{1,2})?)',
        re.IGNORECASE
    )

    # General decimal/integer pattern (avoiding 10-digit phone numbers)
    number_pattern = re.compile(
        r'(?:(?<=\s)|(?<=^)|(?<=[₹$:]))(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?(?=\s|$|[.,\s])'
    )

    # Lines to disregard (taxes, subtotal, change, phone/invoice headers)
    exclude_re = re.compile(
        r'\b(tax\s*invoice|subtotal|sub\s*total|cgst|sgst|igst|vat|tax|discount|cash\s*tendered|cash\s*received|change|phone|mobile|tel|cin|gstin|pin|bill\s*no|inv)\b',
        re.IGNORECASE
    )

    # Pass 1: Check high-priority lines from bottom of receipt up
    for line in reversed(lines):
        if high_priority_re.search(line) and not re.search(r'\b(tax|subtotal|change)\b', line, re.IGNORECASE):
            curr_matches = currency_re.findall(line)
            for m in curr_matches:
                val = _clean_number(m)
                if val is not None:
                    return val

            nums = number_pattern.findall(line)
            parsed_nums = [_clean_number(n) for n in nums if _clean_number(n) is not None]
            if parsed_nums:
                return max(parsed_nums)

    # Pass 2: Check medium-priority lines (TOTAL, NET, AMOUNT)
    for line in reversed(lines):
        if medium_priority_re.search(line) and not exclude_re.search(line):
            curr_matches = currency_re.findall(line)
            for m in curr_matches:
                val = _clean_number(m)
                if val is not None:
                    return val

            nums = number_pattern.findall(line)
            parsed_nums = [_clean_number(n) for n in nums if _clean_number(n) is not None]
            # Prefer decimal amounts over plain integers (e.g. 450.00 over item count 2)
            decimals = [p for p in parsed_nums if not p.is_integer()]
            if decimals:
                return decimals[-1]
            if parsed_nums:
                return parsed_nums[-1]

    # Pass 3: Fallback to any line containing explicit currency symbols (₹, Rs., INR)
    for line in reversed(lines):
        if not exclude_re.search(line):
            curr_matches = currency_re.findall(line)
            for m in curr_matches:
                val = _clean_number(m)
                if val is not None:
                    return val

    return None


def extract_date(text: str) -> str | None:
    """
    Scans receipt text for standard date formats:
    - YYYY-MM-DD / YYYY/MM/DD / YYYY.MM.DD
    - DD-Mon-YYYY / DD Mon YYYY / DD-Mon-YY
    - DD/MM/YYYY / DD-MM-YYYY / DD.MM.YYYY
    - DD/MM/YY / DD-MM-YY
    Returns a normalized YYYY-MM-DD string compatible with HTML <input type="date">, or None.
    """
    if not text:
        return None

    lines = text.splitlines()
    # Prioritize lines containing date labels
    date_labeled_lines = [l for l in lines if re.search(r'\b(date|dt|dated)\b', l, re.IGNORECASE)]
    search_targets = date_labeled_lines + [text]

    month_map = {
        'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
    }

    for target in search_targets:
        # 1. YYYY-MM-DD or YYYY/MM/DD or YYYY.MM.DD
        m = re.search(r'\b(20\d\d)[-/.](0?[1-9]|1[0-2])[-/.](0?[1-9]|[12]\d|3[01])\b', target)
        if m:
            y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                return datetime(y, mo, d).strftime('%Y-%m-%d')
            except ValueError:
                pass

        # 2. DD-Mon-YYYY or DD Mon YYYY or DD-Mon-YY (e.g. 06-Sep-2026, 15 Aug 26)
        m = re.search(r'\b(0?[1-9]|[12]\d|3[01])[-/\s]+([A-Za-z]{3,9})[-/\s,]+(\d{2,4})\b', target)
        if m:
            d_str, mo_str, y_str = m.group(1), m.group(2)[:3].lower(), m.group(3)
            if mo_str in month_map:
                mo = month_map[mo_str]
                d = int(d_str)
                y = int(y_str)
                if y < 100:
                    y += 2000
                try:
                    return datetime(y, mo, d).strftime('%Y-%m-%d')
                except ValueError:
                    pass

        # 3. DD/MM/YYYY or DD-MM-YYYY or DD.MM.YYYY
        m = re.search(r'\b(0?[1-9]|[12]\d|3[01])[-/.](0?[1-9]|1[0-2])[-/.](20\d\d)\b', target)
        if m:
            d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            try:
                return datetime(y, mo, d).strftime('%Y-%m-%d')
            except ValueError:
                pass

        # 4. DD/MM/YY or DD-MM-YY
        m = re.search(r'\b(0?[1-9]|[12]\d|3[01])[-/.](0?[1-9]|1[0-2])[-/.](\d{2})\b', target)
        if m:
            d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3)) + 2000
            try:
                return datetime(y, mo, d).strftime('%Y-%m-%d')
            except ValueError:
                pass

    return None


def parse_receipt_data(raw_text: str) -> dict:
    """
    Coordinator function that parses extracted receipt text into structured data.
    Returns:
        {
            "amount": float | None,
            "date": str | None,   # Formatted as YYYY-MM-DD
            "raw_text": str
        }
    """
    amount = extract_amount(raw_text)
    date = extract_date(raw_text)

    return {
        "amount": amount,
        "date": date,
        "raw_text": raw_text
    }
