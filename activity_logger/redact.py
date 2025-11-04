import cv2
import pytesseract
import re

"""
    
    python3 -m venv path/to/venv
    source path/to/venv/bin/activate
    python3 -m pip install xyz
"""
# Load image
img = cv2.imread("/Users/michaelkim/Desktop/a.png")

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Extract text with bounding boxes
data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

# Regex patterns for PII
patterns = [
    r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",    # SSN
    r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",    # Phone
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}",  # Email
    r"\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b"   # Credit card
]

for i, text in enumerate(data["text"]):
    for pattern in patterns:
        if re.search(pattern, text):
            (x, y, w, h) = (data["left"][i], data["top"][i], data["width"][i], data["height"][i])
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)  # Redact

cv2.imwrite("redacted.png", img)
