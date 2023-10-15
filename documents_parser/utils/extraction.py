import pytesseract
import numpy as np


def extract_text(img: np.ndarray) -> str:
    text = pytesseract.image_to_string(img, lang='rus')
    text = text.strip().replace("\n", " ").strip()
    return text
