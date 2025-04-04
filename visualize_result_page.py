import streamlit as st
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import numpy as np

def load_json_files(folder_input):
    """Load all JSON files and return detailed DataFrame, accuracy summary, and stats"""
    data_list = []
    accuracy_dict = {}

    RESULTS_FOLDER = folder_input.strip()

    # 📊 集計用変数
    total_questions = 0
    total_choices = 0
    total_context_length = 0
    min_choices = float("inf")
    max_choices = 0

    if not os.path.exists(RESULTS_FOLDER):
        st.error(f"❌ Folder '{RESULTS_FOLDER}' not found! Please enter a valid folder name.")
        return pd.DataFrame(), pd.DataFrame(), {}

    for filename in os.listdir(RESULTS_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(RESULTS_FOLDER, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                total_questions += 1
                num_choices = len(data.get("possible_sense_labels", []))
                total_choices += num_choices
                min_choices = min(min_choices, num_choices)
                max_choices = max(max_choices, num_choices)
                total_context_length += len(data.get("context", ""))

                row = {
                    "id": data.get("id", ""),
                    "character": data.get("character", ""),
                    "context": data.get("context", ""),
                    "correct_sense": str(data.get("correct_sense", ""))
                }

                def process_predictions(model_dict, method_label):
                    for model_name, model_results in model_dict.items():
                        if "1" in model_results:
                            result = model_results["1"]
                            predicted_label = str(result.get("answer")) if isinstance(result, dict) else str(result)

                            col_name = f"{method_label}-{model_name}"
                            check_col = f"{col_name}_check"
                            row[col_name] = predicted_label
                            is_correct = predicted_label == row["correct_sense"]
                            row[check_col] = "✅" if is_correct else "❌"

                            if method_label not in accuracy_dict:
                                accuracy_dict[method_label] = {}
                            if model_name not in accuracy_dict[method_label]:
                                accuracy_dict[method_label][model_name] = {"correct": 0, "total": 0}
                            accuracy_dict[method_label][model_name]["total"] += 1
                            if is_correct:
                                accuracy_dict[method_label][model_name]["correct"] += 1

                # PROMPT-based
                for prompt_type, method_data in data.get("prompts", {}).get("method", {}).items():
                    result_data = method_data.get("result", {})
                    if "model" in result_data:
                        process_predictions(result_data["model"], prompt_type)
                    flat_models = {k: v for k, v in result_data.items() if k != "model"}
                    if flat_models:
                        process_predictions(flat_models, prompt_type)

                # BERT-based
                bert_methods = data.get("bert", {}).get("method", {})
                for bert_method, method_data in bert_methods.items():
                    model_dict = method_data.get("result", {}).get("model", {})
                    process_predictions(model_dict, method_label=bert_method)

                data_list.append(row)

    df_details = pd.DataFrame(data_list)

    # Accuracy summary table
    accuracy_data = []
    for method, models in accuracy_dict.items():
        for model, values in models.items():
            correct = values["correct"]
            total = values["total"]
            accuracy = round((correct / total) * 100, 2) if total > 0 else 0
            error_rate = round((total - correct) / total * 100, 2) if total > 0 else 0

            accuracy_data.append({
                "Model": model,
                "Method": method,
                "Correct": correct,
                "Total": total,
                "Accuracy (%)": accuracy
            })

    df_accuracy = pd.DataFrame(accuracy_data)

    # 📌 Summary stats
    avg_choices = round(total_choices / total_questions, 2) if total_questions > 0 else 0
    avg_context_length = round(total_context_length / total_questions, 2) if total_questions > 0 else 0
    summary_info = {
        "total_questions": total_questions,
        "avg_choices": avg_choices,
        "min_choices": min_choices,
        "max_choices": max_choices,
        "avg_context_length": avg_context_length
    }

    return df_details, df_accuracy, summary_info


def plot_accuracy_bar_chart(df_accuracy):
    """Plot bar chart by Method (x-axis), color = Model"""
    if df_accuracy.empty:
        st.write("⚠️ No data available.")
        return

    df_plot = df_accuracy.copy()

    # X-axis order
    method_order = [
        "definition", "definition_token", "example_token",
        "zero_shot", "fixed_few_shot_3", "dynamic_few_shot_3_openAI" #,"dynamic_few_shot_3_guwenBERT"
    ]
    df_plot["Method"] = pd.Categorical(df_plot["Method"], categories=method_order, ordered=True)

    model_order = sorted(df_plot["Model"].unique())
    df_plot["Model"] = pd.Categorical(df_plot["Model"], categories=model_order, ordered=True)

    # Pivot for plotting
    grouped = df_plot.pivot_table(index="Method", columns="Model", values="Accuracy (%)", aggfunc='mean').fillna(0)

    x = np.arange(len(grouped.index))
    width = 0.12
    fig, ax = plt.subplots(figsize=(12, 6))

    model_names = grouped.columns.tolist()
    bars = []
    colors = plt.cm.get_cmap("tab10", len(model_names))

    for i, model in enumerate(model_names):
        offset = (i - len(model_names)/2) * width + width / 2
        bar = ax.bar(x + offset, grouped[model], width, label=model, color=colors(i))
        bars.append(bar)

    ax.set_xlabel("Method", fontsize=14)
    ax.set_ylabel("Accuracy (%)", fontsize=14)
    ax.set_title("Accuracy by Method and Model", fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(grouped.index, rotation=20, ha="right", fontsize=12)
    ax.legend(title="Model", fontsize=10)
    ax.set_ylim(0, 100)

    for bar_group in bars:
        for bar in bar_group:
            yval = bar.get_height()
            if yval > 0:
                ax.text(bar.get_x() + bar.get_width()/2, yval + 1.5, f"{yval:.1f}%", ha='center', va='bottom', fontsize=9)

    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    st.pyplot(fig)


def visualize_result_page():
    st.title("WSD Result Visualization")

    # ✅ ラジオボタンでフォルダ選択
    folder_input = st.radio("Select JSON Folder", ["json_test_4_300", "json_test_5_300", "json_test_6_300", "json_test_7_300", "json_test_16_300", "json_test_17_300", "json_test_18_500"])

    df_details, df_accuracy, summary_info = load_json_files(folder_input)

    if df_details.empty:
        st.write("📂 No JSON files found in the target folder.")
        return

    # 📌 Summary at top
    st.subheader("📌 Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Questions", summary_info["total_questions"])
    col2.metric("Avg. Sense Choices", summary_info["avg_choices"])
    col3.metric("Avg. Context Length", summary_info["avg_context_length"])

    col4, col5 = st.columns(2)
    col4.metric("Min Choices", summary_info["min_choices"])
    col5.metric("Max Choices", summary_info["max_choices"])

    st.subheader("📄 Detailed Data")
    st.dataframe(df_details)

    st.subheader("📊 Accuracy Summary")
    st.dataframe(df_accuracy)

    st.subheader("📈 Accuracy Comparison Chart")
    plot_accuracy_bar_chart(df_accuracy)


if __name__ == "__main__":
    visualize_result_page()
