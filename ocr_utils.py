# Direct proxy to website.ocr_utils for modularity and root-level script execution
from website.ocr_utils import (
    extract_text_from_image,
    extract_amount,
    extract_date,
    parse_receipt_data
)

__all__ = [
    'extract_text_from_image',
    'extract_amount',
    'extract_date',
    'parse_receipt_data'
]
