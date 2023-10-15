import logging
import matplotlib.pyplot as plt
import pandas as pd
from pdf2image import convert_from_path
import cv2
import numpy as np
from documents_parser.utils.extraction import extract_text
from PIL import Image


logger = logging.getLogger("dev")


def line_detector(
    page: Image, threshold: int = 200, min_line_length: int = 300,
    save_line_image: bool = False
) -> list[list]:
    """
    Find horizontal lines on the pruned image.

    :param page: image
    :param threshold: param in HoughLinesP
    :param min_line_length: param in HoughLinesP
    :param save_line_image: save figure with lines or not
    :return:
        list of lines coordinates
    """

    logger.info("Detect lines")
    page = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(page, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 50)
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180,
        threshold, minLineLength=min_line_length, maxLineGap=0
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

    if save_line_image:
        plt.figure(figsize=(15, 20))
        plt.imshow(page)
        plt.savefig("data/img.png")

    return clear_lines


def parse_hat(img: np.ndarray) -> str | None:
    """
    Extract text from hat of the file

    :param img: image
    :return:
        Extracted text
    """
    hat = extract_text(img[0:70, 1600:])
    return hat


def parse_codes(img: np.ndarray, down: int) -> dict:
    """
    Extract text from code block

    :param img: image
    :param down: below line level
    :return:
        dict with parsed code values
    """
    codes = extract_text(img[70: down + 10, 1980:-180])
    codes = codes.split()
    try:
        codes_dict = {
            "ОКУД": codes[1],
            "ОКПО": codes[2],
            "БЕ": codes[3],
        }
    except IndexError:
        codes_dict = {
            "ОКУД": codes[0],
            "ОКПО": codes[1],
            "БЕ": codes[2],
        }
    return codes_dict


def parse_committee(
        img: np.ndarray, lines: list
) -> (str, str, str, str, str):
    """
    Extract committee information from the image

    :param img: image
    :param lines: list of all lines
    :return:
        tuple with 4 main strings
    """
    x1, y, x2, _ = lines[2]
    main_person_profession = extract_text(img[y - 50:y, x1:x1+285])
    main_person_name = extract_text(img[y - 50:y, x1 + 285:x2])
    x1, y, x2, _ = lines[3]
    output = extract_text(img[y-35:y, x1:x2])
    inn = extract_text(img[y+2:y+35, x1+315:x2])
    x1, y, x2, _ = lines[4]
    committee = extract_text(img[y-50:y, x1:x2])

    return main_person_profession, main_person_name, output, inn, committee


def parse_permission(img: np.ndarray, up: int) -> (str, str, str):
    """
    Extract permission data from the image

    :param img: image
    :param up: above line level
    :return:
        tuple with 3 main strings
    """
    x1 = 1500
    x2 = -200
    leader = extract_text(img[up+100:up+150, x1+200:x2-150])
    name = extract_text(img[up+150:up+220, x1+300:x2-50])
    date = extract_text(img[up+240:up+270, x1+100:x2-100])
    return leader, name, date


def parse_act(img: np.ndarray, up: int) -> (int, str):
    """
    Extract act information

    :param img: image
    :param up: above line level
    :return:
        number of act, act date
    """
    x1 = 1040
    x2 = 1300
    text = extract_text(img[up + 140:up + 180, x1:x2])
    text = text.replace("|", " ").replace("—", "")
    number, act_date = text.split()
    return number, act_date


def parse_organisation(lines: list, img: np.ndarray) -> str:
    """
    Extract organisation information

    :param lines: list of all lines
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
    Extract department data from the image

    :param lines: list of all lines
    :param img: image
    :return:
        department, y level
    """
    x1 = lines[0][0]
    y1 = lines[0][1] + 20
    x2 = lines[1][2]
    y2 = lines[1][1]

    structure_department = extract_text(img[y1:y2, x1:x2])
    return structure_department, y2


def ocr_fmu76(
    pdf_path: str | None = None, do_committee: bool = False
) -> pd.DataFrame:
    """
    Convert pdf file of `ФМУ-76` form to string variable.

    :param pdf_path: str, path to pdf file.
    :param do_committee: bool, parse committee or not
    :return:
        All text from file in pdf-pages.
    """

    # Read file
    if pdf_path is None:
        raise ValueError("OCR should work with correct file path.")

    logger.info("Convert PDF file to image.")
    pages = convert_from_path(pdf_path)
    logger.info("Converting PDF file to image finished.")

    # Process first page
    page = pages[0]
    img = np.array(page)
    lines = line_detector(page)

    # Parsing
    logger.info("1. Parsing hat")
    hat = parse_hat(img)
    logger.info("2. Parsing organisation")
    organisation = parse_organisation(lines, img)
    logger.info("3. Parsing department")
    department, codes_y_down = parse_department(lines, img)
    logger.info("4. Parsing permission")
    leader, name, date = parse_permission(img, codes_y_down)
    logger.info("5. Parsing act")
    number, act_date = parse_act(img, codes_y_down)
    logger.info("6. Parsing codes")
    codes_dict = parse_codes(img, codes_y_down)

    if do_committee:
        logger.info("7. Parsing committee")
        long_lines = []
        for line in lines:
            if abs(line[0] - line[2]) > 1300:
                long_lines.append(line)
        main_person_profession, main_person_name, output, inn, committee = parse_committee(img, long_lines)

    # Create report
    report = pd.DataFrame({
        "Тип формы": [hat],
        "Номер акта": [number],
        "Дата акта": [act_date],
        "Организация": [organisation],
        "Структурное подразделение": [department],
        "Утверждено (должность)": [leader],
        "Утверждено (ФИО)": [name],
        "Утверждено (дата)": [date],
        "Коды [Форма по ОКУД]": [codes_dict["ОКУД"]],
        "Коды [Форма по ОКПО]": [codes_dict["ОКПО"]],
        "Коды [Форма, БЕ]": [codes_dict["БЕ"]],
        # "Материально ответственное лицо (должность)": [main_person_profession],
        # "Материально ответственное лицо (ФИО)": [main_person_name],
        # "Направление расхода": [output],
        # "Инвентарный номер ремонтируемого основного средства": [inn],
        # "Комиссия в составе": [committee],
    }).T.rename({0: "Значение"}, axis=1)

    return report
