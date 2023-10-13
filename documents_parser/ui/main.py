import streamlit as st

def run_file_processing(filename):
    print(filename)


def main():
    filename: str | None = None
    st.title("File Uploader")
    check_button = st.button(
        'Check',
        help="Check document",
        on_click=lambda: run_file_processing(filename)
    )
    uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

    if uploaded_file is not None:
        filename = uploaded_file.name
        st.write("Selected file:", filename)

    else:
        st.write("No file selected")


if __name__ == '__main__':
    main()