import os
import json

def merge_json_files(folder_path):
    if not os.path.exists(folder_path):
        print(f"❌ Folder '{folder_path}' does not exist.")
        return

    merged_data = []
    file_count = 0

    # フォルダ内のJSONファイルを処理
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    merged_data.append(data)
                    file_count += 1
                except json.JSONDecodeError:
                    print(f"⚠️ Could not decode JSON file: {filename}")

    # 結果とサマリーを1つのJSONにまとめる
    result = {
        "summary": {
            "total_files": file_count,
            "output_file": f"{folder_path}.json"
        },
        "data": merged_data
    }

    # 結果を保存
    output_file = f"{folder_path}.json"
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(result, outfile, ensure_ascii=False, indent=4)

    print(f"✅ Merged {file_count} JSON files into '{output_file}'.")

if __name__ == "__main__":
    folder_path = input("Enter the folder path: ").strip()
    merge_json_files(folder_path)