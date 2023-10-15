import logging
import matplotlib.pyplot as plt
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from documents_parser.utils.extraction import extract_text
from PIL import Image

logger = logging.getLogger("dev")


def line_detector(
    page: Image, threshold: int = 200,
    save_line_image: bool = False
) -> (list[list], dict):
    """
    Find horizontal lines on the pruned image.

    :param page: image
    :param threshold: param in HoughLinesP
    :param save_line_image: save figure with lines or not
    :return:
        list of lines coordinates, dict with lines info
    """
    logger.info("Detect lines")
    page = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 50)
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180,
        threshold, minLineLength=300, maxLineGap=0
    )

    clear_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = abs(y2 - y1) / abs(x2 - x1 + 0.001)
        if angle < 0.1:
            clear_lines.append([x1, y1, x2, y2])

    sorted_lines = sorted(clear_lines, key=lambda x: x[1])
    clear_lines = [sorted_lines[0]]
    for i, line in enumerate(sorted_lines[1:], 1):
        x1_1 = sorted_lines[i][0]
        y1_1 = sorted_lines[i][1]
        x1_2 = sorted_lines[i][2]
        y1_2 = sorted_lines[i][3]
        x2_1 = sorted_lines[i-1][0]
        y2_1 = sorted_lines[i-1][1]
        x2_2 = sorted_lines[i-1][2]
        y2_2 = sorted_lines[i-1][3]

        eps = 10
        if (
            ((abs(y1_1 - y2_1) < eps) or (abs(y1_2 - y2_2) < eps))
                and
            ((abs(x1_1 - x2_1) < eps) or (abs(x1_2 - x2_2) < eps))
        ):
            continue
        clear_lines.append(line)

    for line in clear_lines:
        cv2.line(
            page,
            (line[0], line[1]),
            (line[2], line[3]),
            (255, 0, 0), 2
        )

    plt.figure(figsize=(15, 20))

    if save_line_image:
        plt.imshow(page)
        plt.savefig("data/img.png")

    img = np.array(page)
    info = {}
    for line in clear_lines:
        x1, y1, x2, y2 = line
        text = extract_text(img[y1-50:y1, 0:x1])
        if (info.get("Через") is None) and ("Через" in text):
            info["Через кого"] = (x1, y1, x2, y2)
        if (info.get("Затребовал") is None) and ("Затребовал" in text):
            info["Затребовал"] = (0, y1, 800, y2)
            info["Разрешил"] = (900, y1, 1600, y2)
        if (info.get("Разрешил") is None) and ("Разрешил" in text):
            info["Разрешил"] = (900, y1, 1600, y2)
            info["Затребовал"] = (0, y1, 800, y2)

    return clear_lines, info


def parse_hat(img: np.ndarray) -> str | None:
    """
    Extract text from hat of the file

    :param img: image
    :return:
        Extracted text
    """
    hat = extract_text(img[30:170, 1000:1600])
    return hat


def parse_number(img: np.ndarray) -> (str, int):
    """
    Parse number of file

    :param img: image
    :return:
        Extracted number, y level
    """
    y = 210
    text = extract_text(img[150:y, 400:1200])
    number = (text.split("№")[1].strip())
    return number, y


def parse_codes(up: int, down: int, img: np.ndarray) -> dict:
    """
    Parse tables with codes

    :param up: above line
    :param down: below line
    :param img: image
    :return:
        dict with codes
    """
    codes = extract_text(img[up: down, -390:-100])
    codes = codes.split()
    codes_dict = {
        "ОКУД": codes[1],
        "ОКПО": codes[3],
        "№": codes[4],
    }
    return codes_dict


def parse_organisation(lines: list, img: np.ndarray) -> str:
    """
    Extract organisation from image

    :param lines: list with all lines
    :param img: image
    :return:
        Extracted text
    """
    x1, y1, x2, y2 = lines[0]
    y1 -= 40

    organisation = extract_text(img[y1:y2, x1:x2])
    return organisation


def parse_department(lines: list, img: np.ndarray) -> (str, int):
    """
    Extract department from image

    :param lines: list with all lines
    :param img: image
    :return:
        Extracted department, y level
    """
    x1 = lines[0][0]
    y1 = lines[0][1]
    x2 = lines[1][2]
    y2 = lines[1][1]

    structure_department = extract_text(img[y1:y2, x1:x2])
    return structure_department, y2


def parse_via_who(img: np.ndarray, info: dict) -> str | None:
    """
    Extract `via whom` data.

    :param img: image
    :param info: dict with lines
    :return:
        Extracted text or None
    """
    if info.get("Через кого") is None:
        return None
    x1, y1, x2, y2 = info.get("Через кого")
    via_who = extract_text(img[y1-70:y1, 0:])
    via_who = via_who.replace("Через кого", "").replace("  ", " ").strip()
    return via_who


def parse_who_get(img: np.ndarray, info: dict) -> str | None:
    """
    Extract `who get` data.

    :param img: image
    :param info: dict with lines
    :return:
        Extracted text or None
    """
    if info.get("Затребовал") is None:
        return None
    x1, y1, x2, y2 = info.get("Затребовал")
    who = extract_text(img[y1-100:y1, 100:800])
    who = who.replace("Затребовал", "").replace("  ", " ").strip()
    if not len(who):
        return None
    return who


def parse_who_get_permission(img: np.ndarray, info: dict) -> str | None:
    """
    Extract `who get permission` data.

    :param img: image
    :param info: dict with lines
    :return:
        Extracted text or None
    """
    if info.get("Разрешил") is None:
        return None
    x1, y1, x2, y2 = info.get("Разрешил")
    who = extract_text(img[y1 - 100:y1, -800:])
    who = who.replace("Разрешил", "").replace("  ", " ").strip()
    return who


def ocr_m11(pdf_path: str | None = None) -> pd.DataFrame:
    """
    Convert pdf file of `M-11` form to string variable.

    :param pdf_path: str, path to pdf file.
    :return:
        All text from file in pdf-pages.
    """

    # Read file
    if pdf_path is None:
        raise ValueError("OCR should work with correct file path.")

    logger.info("Convert PDF file to image.")
    pages = convert_from_path(pdf_path)
    logger.info("Converting PDF file to image finished.")

    # Extract first page
    page = pages[0]
    img = np.array(page)
    lines, info = line_detector(page)

    # Parsing functions
    logger.info("1. Parsing hat")
    hat = parse_hat(img)
    logger.info("2. Parsing number")
    number, codes_y_up = parse_number(img)
    logger.info("3. Parsing organisation")
    organisation = parse_organisation(lines, img)
    logger.info("4. Parsing department")
    department, codes_y_down = parse_department(lines, img)
    logger.info("5. Parsing codes")
    codes_dict = parse_codes(codes_y_up, codes_y_down, img)
    logger.info("6. Parsing via who")
    via_who = parse_via_who(img, info)
    logger.info("7. Parsing who get")
    who_get = parse_who_get(img, info)
    logger.info("8. Parsing who get permission")
    who_get_permission = parse_who_get_permission(img, info)

    # Extract text from all pages
    text = ""
    for page in pages:
        img = np.array(page)
        text += pytesseract.image_to_string(img, lang='rus')

    # Find additional statistics from all text
    doc_info = {}
    for line in text.split("\n"):
        if "Документа сбыта" in line:
            doc_info["Документа сбыта"] = line.split(":")[1].strip()
        if "Документа материала" in line:
            doc_info["Документа материала"] = line.split(":")[1].strip()
        if "Бухгалтерский документ" in line:
            doc_info["Бухгалтерский документ"] = line.split(":")[1].strip()

    # Create report
    report = pd.DataFrame({
        "Тип формы": [hat],
        "Требование-накладная": [number],
        "Организация": [organisation],
        "Структурное подразделение": [department],
        "Коды [Форма по ОКУД]": [codes_dict["ОКУД"]],
        "Коды [Форма по ОКПО]": [codes_dict["ОКПО"]],
        "Коды [Форма, 3 поле]": [codes_dict["№"]],
        "Через кого": [via_who],
        "Затребовал": [who_get],
        "Разрешил": [who_get_permission],
        "Документа сбыта": [doc_info.get("Документа сбыта")],
        "Документа материала": [doc_info.get("Документа материала")],
        "Бухгалтерский документ": [doc_info.get("Бухгалтерский документ")],
    }).T.rename({0: "Значение"}, axis=1)

    return report
