import wandb
import os
import json
wandb.login(
    key='local-d8e9b284a945f5bd44a4f2e396502ac4ac4cd9ff',
    host='http://10.2.31.40:8081'

)
wandb.init(project="agentnet-data-visualization")
data_path = "data/steps/"

files = os.listdir(data_path)
# table = wandb.Table(columns=["article"])
count = 0
for file_id, file in enumerate(files):
    with open(os.path.join(data_path, file, "steps.json"), "r") as f:
        data = json.load(f)
    
    steps = data["steps"]
    html = f"<h1>{data['page']['title']}</h1>"
    html += f"<a href='{data['page']['link']}'>Link</a>"
    for step_id, step in enumerate(steps):
        html += f"<h2>Step {step_id + 1}</h2>"
        html += f"<p>{step['text']}</p>"
        if "image_url" in step:
            html += f"<img src='{step['image_url']}'>"
    wandb.log(
        {
            # f"{data['page']['link']}": wandb.Html(html)，
            "logs": wandb.Html(html)
        }
    )
    count += 1
    if count == 100:
        break
    
    