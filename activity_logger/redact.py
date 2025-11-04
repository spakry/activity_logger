import cv2
import pytesseract
import re
from typing import List, Dict, Any, Union
import numpy as np
from PIL import Image

PII_PATTERNS: List[str] = [
    r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b",          # SSN
    r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",          # Phone
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}",  # Email
    r"\b\d{4}\s\d{4}\s\d{4}\s\d{4}\b",         # Credit card
]

def redact_image(image: Union[np.ndarray, Image.Image]) -> Image.Image:
    """Redact PII from an image using OCR.
    
    Args:
        image: PIL Image or numpy array to redact
    
    Returns:
        Redacted PIL Image, or original image if redaction fails
    """
    try:
        if isinstance(image, Image.Image):
            # Handle RGBA images
            img_array = np.array(image)
            if len(img_array.shape) == 3 and img_array.shape[2] == 4:
                # RGBA - convert RGB portion to BGR
                rgb_array = img_array[:, :, :3]
                img = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)
                alpha_channel = img_array[:, :, 3]
            elif len(img_array.shape) == 3:
                # RGB - convert to BGR
                img = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                alpha_channel = None
            else:
                # Grayscale or other format, return original
                return image
        elif isinstance(image, np.ndarray):
            img = image.copy()
            alpha_channel = None
        else:
            raise ValueError("Input must be a PIL.Image.Image or numpy.ndarray")

        # --- Preprocess ---
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Extract text with bounding boxes
        data: Dict[str, List[Any]] = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

        # --- Redact matched patterns ---
        for i, text in enumerate(data["text"]):
            if not text.strip():
                continue
            for pattern in PII_PATTERNS:
                if re.search(pattern, text):
                    x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), -1)

        # --- Convert back to PIL Image before returning ---
        redacted_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        if alpha_channel is not None:
            # Reconstruct RGBA image
            redacted_rgba = np.dstack([redacted_rgb, alpha_channel])
            redacted_pil = Image.fromarray(redacted_rgba, mode='RGBA')
        else:
            redacted_pil = Image.fromarray(redacted_rgb, mode='RGB')
        
        return redacted_pil
    except Exception as e:
        print(f"Redaction failed: {e}, using original image")
        # Return original image if it's PIL, otherwise convert numpy to PIL
        if isinstance(image, Image.Image):
            return image
        else:
            return Image.fromarray(image)