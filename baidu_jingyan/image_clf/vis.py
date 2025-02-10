import wandb
import os
import json
import pandas as pd
import base64
wandb.login(
    key='local-d8e9b284a945f5bd44a4f2e396502ac4ac4cd9ff',
    host='http://10.2.31.40:8081'

)
wandb.init(project="agentnet-data-visualization")
data_path = "data/steps/"

image_data = pd.read_csv("data/image_classification_result.csv")

# table = wandb.Table(columns=["article"])
count = 0
for file_id, row in image_data.iterrows():
    
    image_path = row["image_id"]
    prediction = row["is_gui"]
    # encode the image to base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    html = f"<h1>Image {image_path}</h1>"
    html += f"<p>Prediction: {prediction}</p>"
    html += f"<img src='data:image/jpeg;base64,{encoded_string}'>"
    wandb.log(
        {
            # f"{data['page']['link']}": wandb.Html(html)，
            "logs": wandb.Html(html)
        }
    )
