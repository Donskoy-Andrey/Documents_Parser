import pandas as pd
import streamlit as st
from pathlib import Path
import base64
import random
from documents_parser.ui.validator import validate_tables_m11, validate_raw_data_m11
from documents_parser.parser.ocr_m11_scripts import ocr_m11
from documents_parser.parser.table_parser import table_ocr_m

SRC_PATH = Path(__file__).parent / "src"
DOWNLOAD_FILENAME = Path("data/file.pdf")


def test():
    df = pd.read_csv(SRC_PATH / "report.csv", index_col=0)
    accepted = random.randint(0, 1)
    return df


class Gui:
    def __init__(self):
        """
        initialize the class Gui
        """
        st.set_page_config(layout='wide')

        self.uploaded_file = None
        self.button_disabled = True
        self.check_button: st.button or None = None
        self.head_container = st.container()

        self.upload_container = st.container()
        self.result_container = st.container()
        self.result_container.write("")
        self.button_container = st.container()
        self.data_container = st.container()
        self.data_container.write("")

        self.__draw_gui()

    def __draw_gui(self) -> None:
        """
        draw base widgets of UI
        :return: None
        """
        with self.head_container:
            title, logo = st.columns([5, 1])
            title.title("Прием учетных документов «AAA Team»")
            # we.image(str(SRC_PATH / "img.png"), width=100, output_format="PNG")
            logo.image(str(SRC_PATH / "logo.png"), width=150, output_format="PNG")
            self.option = st.selectbox(
                "Выберите тип документа",
                ("М-11", "ФМУ-76"),
                index=None,
                placeholder="Выберите тип документа...",
            )

        self.draw_choose_file()

        with self.button_container:
            self.check_button = st.button(
                'Проверить',
                help="Проверить документ",
                on_click=lambda: self.run_file_processing(),
                disabled=self.button_disabled
            )

    def draw_choose_file(self) -> None:
        """
        Draw choose file widget
        :return: None
        """
        with self.upload_container:
            self.uploaded_file = st.file_uploader(
                "Выберите файл",
                type=["pdf"],
                accept_multiple_files=False
            )

        if self.uploaded_file is not None:
            filename = self.uploaded_file.name
            with self.button_container:
                st.write("Выбранный файл:", filename)
            if self.option:
                self.button_disabled = False

        else:
            st.write("Не выбран файл")

    def run_file_processing(self) -> None:
        """
        Activate functions, reaction on click of check_button
        :return: None
        """
        self.button_disabled = True

        with open(DOWNLOAD_FILENAME, 'wb+') as f:
            # save file to local machine
            f.write(self.uploaded_file.read())
        # gif_path = "https://donskow.com/g"
        gif_path = "https://donskow.com/train4"
        with self.button_container:
            # loading gif :)
            gif_runner = st.image(gif_path)
        print(f"{self.option=}")
        df = ocr_m11(pdf_path=str(DOWNLOAD_FILENAME))
        df_list = table_ocr_m(path=str(DOWNLOAD_FILENAME))

        gif_runner.empty()  # finish gif
        self.button_container.empty()
        self.draw_results_m11(df, df_list)
        self.uploaded_file = None

    def draw_results_m11(self, df: pd.DataFrame, df_list: list) -> None:
        """
        draw results of document parser func
        :param df: df with results of from parser func
        :param is_accept: returned status of parser func
        :param df_list: returned list of dataframes with table data
        :return:
            None
        """

        unvalidated_row, reasons_row = validate_raw_data_m11(df)
        is_accept = len(unvalidated_row)

        unvalidated_list = []
        reasons_list = []
        for dataframe in df_list:
            unvalidated_t, reason_t = validate_tables_m11(dataframe)
            unvalidated_list.append(unvalidated_t)
            is_accept += len(unvalidated_t)
            reasons_list.append(reason_t)

        def highlight_survived(s):
            return [''] * len(s) if s["Название"] not in unvalidated_row else [
                                                                                  'background-color: tomato;text-color: black;'] * len(
                s)

        def color_survived(val, df, unvalidated):
            color = 'background-color: tomato;text-color: black;'
            for coord in unvalidated:
                index, col = coord[0], coord[1]
                if df.loc[index, col] == val:
                    return color
            return ''



        if df is not None:
            if is_accept == 0:
                self.data_container.markdown(
                    '<h2 style="color:white;background-color:green;text-align:center">Принято</h2>',
                    unsafe_allow_html=True)
                # self.data_container.markdown('_____', )
            else:
                self.data_container.markdown(
                    '<h2 style="color:white;background-color:red;text-align:center">Отклонено</h2>',
                    unsafe_allow_html=True)

        with self.data_container:
            if len(reasons_row) != 0:
                if len(reasons_row) < 2:
                    st.markdown('<h1 style="text-align:center">Причина:<h1>', unsafe_allow_html=True)
                else:
                    st.markdown('<h1 style="text-align:center">Причины:<h1>', unsafe_allow_html=True)
                for reason in reasons_row:
                    st.markdown(f'- {reason}')
                for reasons in reasons_list:
                    for reason in reasons:
                        st.markdown(f'- {reason}')

        self.data_container.markdown('_____', )
        df = df.reset_index().rename({"index": "Название"}, axis=1)

        self.data_container.markdown('<h1 style="text-align:center">Отчет<h1>', unsafe_allow_html=True)
        if isinstance(df, pd.DataFrame):
            self.data_container.dataframe(
                # df.style.set_properties(**{"background-color": "black", "color": "lawngreen"}),
                df.style.apply(highlight_survived, axis=1),
                use_container_width=True,
                height=500,
                hide_index=True
            )
        with self.data_container:
            for i in range(len(df_list)):
                dataframe = df_list[i]
                unvalidated_t = unvalidated_list[i]
                reason_t = reasons_list[i]
                try:
                    st.dataframe(dataframe.style.map(lambda x: color_survived(x, dataframe, unvalidated_t)),
                                 hide_index=True)

                except Exception as e:
                    print(e)
                    raise e

    def displayPDF(self, file):
        # Opening file from file path
        with open(file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        # Embedding PDF in HTML
        pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
        with self.button_container:
            # Displaying File
            st.markdown(pdf_display, unsafe_allow_html=True)


def main():
    ui = Gui()


if __name__ == '__main__':
    main()
