# メインファイル: visualize_result_page.py
import streamlit as st
from components.data_loader import load_json_files
from components.visualizations import plot_accuracy_bar_chart
from components.analysis import calculate_agreement_rate
from components.json_search import search_json_file, display_json_result
from components.ui_components import display_summary, display_agreement_rate_ui, display_json_search_ui
from components.config import FOLDER_MAPPING

def visualize_result_page():
    st.title("Historical Chinese WSD Test Result Visualization")

    # フォルダ選択
    selected_display_name = st.radio("Select JSON Folder", list(FOLDER_MAPPING.keys()))
    folder_input = FOLDER_MAPPING[selected_display_name]

    # データロード
    df_details, df_accuracy, summary_info = load_json_files(folder_input)

    if df_details.empty:
        st.write("📂 No JSON files found in the target folder.")
        return

    # サマリー表示
    display_summary(summary_info)

    # 詳細データ表示
    st.subheader("📄 Detailed Data")
    st.dataframe(df_details)

    # 精度サマリー表示
    st.subheader("📊 Accuracy Summary")
    st.dataframe(df_accuracy)

    # 精度比較グラフ表示
    st.subheader("📈 Accuracy Comparison Chart")
    fig = plot_accuracy_bar_chart(df_accuracy, summary_info["avg_choices"])
    st.pyplot(fig)

    # 一致率計算UI表示
    model1, model2 = display_agreement_rate_ui(df_details)
    
    if model1 and model2:
        df_comparison, agreement_rate = calculate_agreement_rate(df_details, model1, model2)
        st.write(f"### Agreement Rate: {agreement_rate}%")
        st.dataframe(df_comparison)

    # JSON検索UI表示
    search_id, search_pressed = display_json_search_ui()
    
    if search_pressed and search_id:
        json_data = search_json_file(folder_input, search_id)
        if json_data:
            st.success(f"✅ Found JSON with ID: {search_id}")
            display_json_result(json_data)
        else:
            st.error(f"❌ No JSON found with ID: {search_id}")


if __name__ == "__main__":
    visualize_result_page()