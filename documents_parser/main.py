from sys import argv
from .parser.ocr_scripts import ocr


def main():
    filename = None
    if len(argv) == 2:
        filename = argv[1]
    ocr(pdf_path=filename)


if __name__ == "__main__":
    main()
