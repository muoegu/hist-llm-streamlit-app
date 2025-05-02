import streamlit as st
import pandas as pd

def calculate_agreement_rate(df_details, model1, model2):
    """Calculate Agreement Rate between two models"""
    if model1 not in df_details.columns or model2 not in df_details.columns:
        st.error(f"❌ Selected models '{model1}' or '{model2}' not found in the data.")
        return pd.DataFrame(), 0

    # Add 'id', models, and their '_check' columns to the comparison DataFrame
    check_col1 = f"{model1}_check"
    check_col2 = f"{model2}_check"
    columns_to_include = ["id", model1, check_col1, model2, check_col2]
    columns_to_include = [col for col in columns_to_include if col in df_details.columns]  # Ensure columns exist

    df_comparison = df_details[columns_to_include].copy()
    df_comparison["Agreement"] = df_comparison[model1] == df_comparison[model2]

    # Calculate Agreement Rate
    agreement_rate = round(df_comparison["Agreement"].mean() * 100, 2)

    return df_comparison, agreement_rate