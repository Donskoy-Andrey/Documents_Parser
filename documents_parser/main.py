from sys import argv
from .parser.ocr_scripts import ocr
from .parser.table_parser import table_ocr_m


def main():
    filename = None
    if len(argv) == 2:
        filename = argv[1]
    ocr(pdf_path=filename)
    table_ocr_m(path=filename)


if __name__ == "__main__":
    main()

