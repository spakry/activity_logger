import cv2
import pytesseract
import re
import sys
from pathlib import Path


PII_PATTERNS = [
    r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",          # SSN
    r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",          # Phone
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}",  # Email
    r"\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b",         # Credit card
]


def redact_image(input_path: str, output_path: str) -> None:
    # Load and preprocess
    img = cv2.imread(input_path)
    if img is None:
        raise FileNotFoundError(f"Could not read image: {input_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # OCR extract bounding boxes
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

    # Scan for matches and redact
    for i, text in enumerate(data["text"]):
        if not text.strip():
            continue
        for pattern in PII_PATTERNS:
            if re.search(pattern, text):
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)

    # Save redacted image
    cv2.imwrite(output_path, img)
    print(f"Redacted image saved to {output_path}")