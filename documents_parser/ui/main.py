import time

import streamlit as st
from pathlib import Path
from PIL import Image

SRC_PATH = Path(__file__).parent / "src"
DOWNLOAD_FILENAME = Path("documents_parser/incoming_files/file.pdf")

def test():
    time.sleep(5)

class Gui:
    def __init__(self):
        st.set_page_config(layout='wide')
        self.uploaded_file = None
        # self.button_status = ButtonStatus(disabled=True)
        self.button_disabled = True
        self.check_button: st.button or None = None
        self.draw_gui()

    def draw_gui(self):
        # title, logo = st.columns(2)
        title, logo = st.columns([5, 1])
        title.title("File Uploader by \"AAA_Team\"")
        logo.image(str(SRC_PATH / "logo.png"), width=150, output_format="PNG")
        self.draw_choose_file()
        # st.image(str(SRC_PATH / "dance.gif"), output_format='GIF')
        self.check_button = st.button(
            'Check',
            help="Check document",
            on_click=lambda: self.run_file_processing(),
            disabled=self.button_disabled
        )

    def draw_choose_file(self):
        self.uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf"],
            accept_multiple_files=False
        )
        if self.uploaded_file is not None:
            filename = self.uploaded_file.name
            # uploaded_file.write('')
            st.write("Selected file:", filename)
            self.button_disabled = False

        else:
            st.write("No file selected")

    def run_file_processing(self):
        self.button_disabled = True
        with open(DOWNLOAD_FILENAME, 'wb+') as f:
            f.write(self.uploaded_file.read())
        print(self.uploaded_file.name)
        gif_path = "https://donskow.com/g"

        gif_runner = st.image(gif_path)
        test()
        gif_runner.empty()
        self.uploaded_file = None


def main():
    ui = Gui()


if __name__ == '__main__':
    main()
