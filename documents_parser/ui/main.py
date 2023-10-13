import streamlit as st

def main():
    st.title("File Uploader")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf"])

    if uploaded_file is not None:
        file_name = uploaded_file.name
        st.write("Selected file:", file_name)
        butto
    else:
        st.write("No file selected")


if __name__ == '__main__':
    main()