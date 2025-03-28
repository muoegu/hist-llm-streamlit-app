import streamlit as st
from summary_page import summary_page
from visualize_result_page import visualize_result_page

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("", (
        "Result",
        "Summary"
        
    ))

    if page == "Result":
        visualize_result_page()
    elif page == "Summary":
        summary_page() 

if __name__ == "__main__":
    main()
