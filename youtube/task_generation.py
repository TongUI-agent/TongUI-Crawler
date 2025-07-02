from typing import List
from openai import AzureOpenAI
import os
import time

MODEL = ""
API_KEY = ""
API_VERSION = ""
API_BASE = ""
REGION = ""
ENDPOINT = f"{API_BASE}/{REGION}"

client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT,
)

def expand_tasks_with_llm(app: str, seed_tasks: List[str]) -> List[str]:
    prompt = f"""
You're given a list of example user tasks for the application '{app}': {seed_tasks}.
Please expand this list by suggesting more relevant and diverse user tasks.

Output Format:
- Return only the task descriptions, one per line.
- Do not include numbering, bullets, or extra formatting.

Example Output:
open a new window
close all tabs
open incognito mode
"""
    
    for i in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt.strip()},
                        ],
                    }
                ],
                max_tokens=200,
            )
            expanded_text = response.choices[0].message.content

            expanded_tasks = [line.strip() for line in expanded_text.strip().split('\n') if line.strip()]
            all_tasks = list(set(seed_tasks + expanded_tasks))
            return all_tasks
        except Exception as e:
            print(f"Error in API call (attempt {i+1}/3): {str(e)}")
            time.sleep(5)

    return seed_tasks

def save_tasks_to_file(app: str, tasks: List[str], output_dir: str = "op"):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"{app}_operations.txt")
    
    formatted_tasks = [task.capitalize() for task in tasks]
    
    with open(file_path, "w", encoding="utf-8") as f:
        for task in formatted_tasks:
            f.write(f"{task}\n")
    print(f"Saved {len(formatted_tasks)} tasks to {file_path}")

if __name__ == "__main__":
    task_seeds = {
        "word": ["change font size", "insert table", "save document"],
        "chrome": ["open new tab", "bookmark page", "clear history"],
    } 
    output_dir = "op"

    for app, seeds in task_seeds.items():
        expanded_tasks = expand_tasks_with_llm(app, seeds)
        save_tasks_to_file(app, expanded_tasks, output_dir)

