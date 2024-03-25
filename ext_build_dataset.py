import json
import random
from typing import Optional

def process_and_split_json(input_file: str, output_dir: str, split: float = 0.0):
    # Step 1: Read the JSON file
    with open(input_file, 'r') as file:
        data = json.load(file)
    
    # Step 2 & 3: Rename "qid" to "id" and keep only "id", "question", "answer"
    # processed_data = [
    #     {'id': item['qid'], 'question': item['question'], 'answer': int(item['answer'])}
    #     for item in data
    # ]
    processed_data = []
    for item in data:
        processed_item = {'id': item['qid'], 'question': item['question']}
        if 'answer' in item:
            processed_item['answer'] = int(item['answer'])
        processed_data.append(processed_item)
    
    # Step 4: Randomly shuffle the data
    random.shuffle(processed_data)
    
    # Step 5: Optionally split the data
    split_index = int(len(processed_data) * split) if split else None
    if split_index:
        data_part_1 = processed_data[:split_index]
        data_part_2 = processed_data[split_index:]
    else:
        data_part_1 = processed_data
        data_part_2 = []
    
    # Step 6: Save the data to jsonl files
    part_1_path = f"{output_dir}/data_part_1.jsonl"
    with open(part_1_path, 'w') as file:
        for item in data_part_1:
            file.write(json.dumps(item) + '\n')
    
    if data_part_2:
        part_2_path = f"{output_dir}/data_part_2.jsonl"
        with open(part_2_path, 'w') as file:
            for item in data_part_2:
                file.write(json.dumps(item) + '\n')
        return part_1_path, part_2_path
    
    return part_1_path, None

# Example usage
input_file = '/workspace/data/consistent-CoT-distillation/raw_data/strategyQA/strategyqa_test.json'
output_dir = '/workspace/consistent-CoT-distillation/data/strategyQA'
split_ratio = 0.0

process_and_split_json(input_file, output_dir, split_ratio)
