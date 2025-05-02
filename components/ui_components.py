import streamlit as st

def display_summary(summary_info):
    """Display summary metrics in a nice layout"""
    st.subheader("📌 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", summary_info["total_questions"])
    col2.metric("Avg. Sense Choices", summary_info["avg_choices"])
    col3.metric("Avg. Context Length", summary_info["avg_context_length"])

    col4, col5 = st.columns(2)
    col4.metric("Min Choices", summary_info["min_choices"])
    col5.metric("Max Choices", summary_info["max_choices"])

def display_agreement_rate_ui(df_details):
    """Display UI for agreement rate calculation"""
    st.subheader("🤝 Agreement Rate Between Models")
    model_columns = [col for col in df_details.columns if not col.endswith("_check") and col not in ["id", "character", "context", "correct_sense"]]
    if len(model_columns) < 2:
        st.write("⚠️ Not enough models to compare.")
        return None, None
    
    model1 = st.selectbox("Select Model 1", model_columns, index=0)
    model2 = st.selectbox("Select Model 2", model_columns, index=1)
    
    return model1, model2

def display_json_search_ui():
    """Display UI for JSON search"""
    st.subheader("🔍 Search for JSON by ID")
    search_id = st.text_input("Enter ID to search:", "")
    search_pressed = st.button("Search")
    
    return search_id, search_pressed