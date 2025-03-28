import streamlit as st
from visualize_result_page import visualize_result_page

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("", (
        "Result"
    ))

    if page == "Result":
        visualize_result_page()
    elif page == "Result":
        visualize_result_page() 

if __name__ == "__main__":
    main()
