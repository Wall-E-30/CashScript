#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Tesseract OCR engine and English language pack
apt-get update && apt-get install -y tesseract-ocr tesseract-ocr-eng

# Install Python dependencies
pip install -r requirements.txt