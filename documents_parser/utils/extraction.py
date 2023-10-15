import pytesseract
import numpy as np


def extract_text(img: np.ndarray) -> str:
    """
    Extract text from the image using Tesseract

    :param img: image
    :return:
        Extracted text
    """
    text = pytesseract.image_to_string(img, lang='rus')
    text = text.strip().replace("\n", " ").strip()
    return text
