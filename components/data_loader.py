# 複数のコンポーネントファイルに分割

# 1. data_loader.py - データ読み込み関連
import streamlit as st
import pandas as pd
import os
import json

def load_json_files(folder_input):
    """Load all JSON files and return detailed DataFrame, accuracy summary, and stats"""
    data_list = []
    accuracy_dict = {}

    RESULTS_FOLDER = folder_input.strip()

    # 📊 集計用変数
    total_questions = 0
    total_choices = 0
    total_possible_sense_labels = 0  
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
                possible_sense_labels = data.get("possible_sense_labels", [])
                num_choices = len(possible_sense_labels)
                total_choices += num_choices
                total_possible_sense_labels += num_choices  
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

            accuracy_data.append({
                "Model": model,
                "Method": method,
                "Correct": correct,
                "Total": total,
                "Accuracy (%)": accuracy
            })

    df_accuracy = pd.DataFrame(accuracy_data)

    # 📌 Summary stats
    avg_choices = round(total_possible_sense_labels / total_questions, 2) if total_questions > 0 else 0  
    avg_context_length = round(total_context_length / total_questions, 2) if total_questions > 0 else 0
    summary_info = {
        "total_questions": total_questions,
        "avg_choices": avg_choices,
        "min_choices": min_choices,
        "max_choices": max_choices,
        "avg_context_length": avg_context_length
    }

    return df_details, df_accuracy, summary_info