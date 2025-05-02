import streamlit as st
import os
import json

def search_json_file(folder_input, search_id):
    """Search for a specific JSON file by ID and display its content"""
    if not search_id:
        return None
        
    RESULTS_FOLDER = folder_input.strip()
    if not os.path.exists(RESULTS_FOLDER):
        st.error(f"❌ Folder '{RESULTS_FOLDER}' not found!")
        return None
    
    for filename in os.listdir(RESULTS_FOLDER):
        if filename.endswith(".json"):
            file_path = os.path.join(RESULTS_FOLDER, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if str(data.get("id", "")).strip() == search_id.strip():
                    return data
    
    return None

def display_json_result(json_data):
    """Display JSON search result in structured format"""
    if not json_data:
        return
    
    # Basic Information
    st.write("### Basic Information")
    st.write(f"**Character:** {json_data.get('character', '')}")
    st.write(f"**Correct Sense:** {json_data.get('correct_sense', '')}")
    st.write(f"**Possible Senses:** {', '.join(str(item) for item in json_data.get('possible_sense_labels', []))}")
    
    # Context
    st.write("### Context")
    st.write(json_data.get('context', ''))
    
    # Model Predictions
    st.write("### Model Predictions")
    
    # PROMPT-based results
    if "prompts" in json_data and "method" in json_data["prompts"]:
        for prompt_type, method_data in json_data["prompts"]["method"].items():
            st.write(f"#### {prompt_type}")
            result_data = method_data.get("result", {})
            
            # Display examples for dynamic few-shot methods
            if prompt_type in ["dynamic_few_shot_3_openAI", "dynamic_few_shot_10_openAI"]:
                if "examples" in method_data:
                    with st.expander(f"Show Examples for {prompt_type}"):
                        st.json(method_data["examples"])
            
            if "model" in result_data:
                for model_name, model_results in result_data["model"].items():
                    if "1" in model_results:
                        result = model_results["1"]
                        predicted = result.get("answer") if isinstance(result, dict) else result
                        is_correct = str(predicted) == str(json_data.get("correct_sense", ""))
                        st.write(f"**{model_name}**: {predicted} {'✅' if is_correct else '❌'}")
    
    # BERT-based results
    if "bert" in json_data and "method" in json_data["bert"]:
        st.write("#### BERT-based Methods")
        for bert_method, method_data in json_data["bert"]["method"].items():
            st.write(f"**{bert_method}**:")
            model_dict = method_data.get("result", {}).get("model", {})
            for model_name, model_results in model_dict.items():
                if "1" in model_results:
                    result = model_results["1"]
                    predicted = result.get("answer") if isinstance(result, dict) else result
                    is_correct = str(predicted) == str(json_data.get("correct_sense", ""))
                    st.write(f"  - **{model_name}**: {predicted} {'✅' if is_correct else '❌'}")
    
    # Raw JSON Data
    with st.expander("Show Raw JSON Data"):
        st.json(json_data)