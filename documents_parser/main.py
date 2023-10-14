from sys import argv
from .parser.ocr_m11_scripts import ocr_m11
from .parser.ocr_fmu76_scripts import ocr_fmu76
from .parser.table_parser import table_ocr
import logging


logger = logging.getLogger("dev")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


def main():
    filename = None
    if len(argv) == 2:
        filename = argv[1]
    # ocr_m11(pdf_path=filename)
    # table_ocr(path=filename)

    ocr_fmu76(pdf_path=filename)
    # table_ocr(path=filename)


if __name__ == "__main__":
    main()

