import os
import json
from collections import deque
import re

def format_box(box):
    box = eval(box)
    box = [round(box[0] / 1000, 2), round(box[1] / 1000, 2)]
    return box

def function_parser_desktop(function_str, app_type):

    func_name_proj = {
        "click": "CLICK",
        "left_double": "LEFT_CLICK_DOUBLE",
        "right_single": "RIGHT_CLICK_SINGLE",
        "drag": "DRAG",
        "hotkey": "HOT_KEY",
        "type": "INPUT",
        "scroll": "SCROLL",
        "finished": "FINISH",
        "wait": "WAIT",
        "call_user": "CALL_USER",
    }
    def click(start_box):
        start_box = format_box(start_box)
        args = {"action": "CLICK", "value": None, "position": start_box}
        return "click", args
    
    def left_double(start_box):
        start_box = format_box(start_box)
        args = {"action": "LEFT_CLICK_DOUBLE", "value": None, "position": start_box}
        return "left_double", args
    
    def right_single(start_box):
        start_box = format_box(start_box)
        args = {"action": "RIGHT_CLICK_SINGLE", "value": None, "position": start_box}
        return "right_single", args
    
    def drag(start_box, end_box):
        start_box = format_box(start_box)
        end_box = format_box(end_box)
        args = {"action": "DRAG", "value": None, "position": [start_box, end_box]}
        return "drag", args
    
    def hotkey(key):
        args = {"action": "HOT_KEY", "value": key, "position": None}
        return "hotkey", args
    
    def type(content):
        args = {"action": "INPUT", "value": content, "position": None}
        return "type", args
    
    def scroll(start_box, direction):
        start_box = format_box(start_box)
        args = {"action": "SCROLL", "value": direction, "position": start_box}
        return "scroll", args
    
    def finished():
        args = {"action": "FINISH", "value": None, "position": None}
        return "finished", args
    
    def wait():
        args = {"action": "WAIT", "value": None, "position": None}
        return "wait", args
    
    def call_user():
        args = {"action": "CALL_USER", "value": None, "position": None}
        return "call_user", args
    function_str = function_str.split("\n")
    function_str = [i.strip() for i in function_str if i.strip()]
    function_str = [i for i in function_str if len(i) > 0]

    func_names_outputs = []
    func_args_outputs = []
    for func in function_str:
        try:
            func_name, func_args = eval(func)
        except:
            func_name = "error"
            func_args = {"action": "ERROR", "value": None, "position": None}
        func_names_outputs.append(func_name)
        func_args_outputs.append(func_args)
    if len(func_names_outputs) == 1:
        return func_names_outputs, func_args_outputs[0]
    else:
        return func_names_outputs, func_args_outputs

def function_parser_mobile(function_str, app_type):
    def click(start_box):
            start_box = format_box(start_box)
            args = {"action": "TAP", "value": None, "position": start_box}
            return "click", args
        
    def finished(content=None):
        args = {"action": "FINISH", "value": content, "position": None}
        return "finished", args
    
    def long_press(start_box, time):
        start_box = format_box(start_box)
        args = {"action": "LONG_PRESS", "value": int(time), "position": start_box}
        return "long_press", args
    
    def press_home():
        args = {"action": "PRESS_HOME", "value": None, "position": None}
        return "press_home", args
    
    def press_back():
        args = {"action": "PRESS_BACK", "value": None, "position": None}
        return "press_back", args
    
    def type(content):
        args = {"action": "INPUT", "value": content, "position": None}
        return "type", args

    def scroll(start_box, end_box):
        start_box = format_box(start_box)
        end_box = format_box(end_box)
        args = {"action": "SWIPE", "value": None, "position": [start_box, end_box]}
        return "scroll", args
    function_str = function_str.split("\n")
    function_str = [i.strip() for i in function_str if i.strip()]
    function_str = [i for i in function_str if len(i) > 0]
    func_names_outputs = []
    func_args_outputs = []
    for func in function_str:
        try:
            func_name, func_args = eval(func)
        except:
            func_name = "error"
            func_args = {"action": "ERROR", "value": None, "position": None}
        func_names_outputs.append(func_name)
        func_args_outputs.append(func_args)
    if len(func_names_outputs) == 1:
        return func_names_outputs, func_args_outputs[0]
    else:
        return func_names_outputs, func_args_outputs

def sort_key(file_name):
    return [int(x) if x.isdigit() else x for x in re.split(r'(\d+)', file_name)]

def process_single_video(action_path, image_path, video_name, device_type, output_json_path):
    video_output_json = []
    segments = sorted(os.listdir(action_path), key=sort_key)
    task = video_name.split("~~")[0]

    historical_actions = deque(maxlen=2)
    historical_images = deque(maxlen=2)

    for _, segment_name in enumerate(segments):
        thought_file_path = os.path.join(action_path, segment_name)
        image_file_path = os.path.join(image_path, segment_name.replace('segment_', '').replace('_thought.txt', '.png'))
        action_file_path = os.path.join(action_path, segment_name.replace('_thought.txt', '.txt'))
    
        if os.path.isfile(thought_file_path) and os.path.isfile(image_file_path) and os.path.isfile(action_file_path):
            with open(action_file_path, 'r', encoding='utf-8') as f:
                actions = f.read()

            try:
                with open(thought_file_path, 'r', encoding='utf-8') as f:
                    thought = f.read()

                action_index = thought.find("Action: ")

                if action_index != -1:
                    thought = thought[:action_index].strip()
            except:
                thought = ""

            if "Desktop" in device_type:
                action_type, actions = function_parser_desktop(actions, "Desktop")
                actions = f"Thought: {thought}\nAction: {json.dumps(actions)}"
                segment_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": f'''You are an assistant trained to navigate the website screen. 
Given a task instruction, a screen observation, and an action history sequence, 
output the next action and wait for the next observation. 
Here is the action space:

1. `CLICK`: Click on an element, value is not applicable and the position [x,y] is required. 
2. `INPUT`: Type a string into an element, value is a string to type and the position [x,y] is required. 
3. `SCROLL`: Scroll the screen, value is the direction to scroll and the position is start position of the scroll operation.
4. `LEFT_CLICK_DOUBLE`: Left click on an element twice, value is not applicable and the position [x,y] is required.
5. `RIGHT_CLICK_SINGLE`: Right click on an element once, value is not applicable and the position [x,y] is required.
6. `DRAG`: Drag the cursor to the specified position with the left button pressed. Value is not applicable and position [[x1,y1], [x2,y2]] is the start and end position of the drag operation.
7. `HOT_KEY`: Press a hot key, value is the hot key and the position is not applicable.
8. `WAIT`: Wait for 5 seconds, and take a screenshot to check for any changes. Value and position are not applicable.
9. `FINISH`: Finish the task. Value and position are not applicable.

Format your response as:
Thought: <your reasoning process>
Action: <the next action>

Format the action as a JSON object with the following keys:
{{"action": "ACTION_TYPE", "value": "element", "position": [x,y]}}
You can output multiple actions at once, and use JSON array to represent multiple actions.
If value or position is not applicable, set it as `None`.
Position might be [[x1,y1], [x2,y2]] if the action requires a start and end position.
Position represents the relative coordinates on the screenshot and should be scaled to a range of 0-1.
Task: {task}
<image>'''
                        },
                        {
                            "role": "assistant",
                            "content": actions
                        }
                    ],
                    "images": [image_file_path]
                }
            elif "Mobile" in device_type:
                action_type, actions = function_parser_mobile(actions, "Mobile")
                actions = f"Thought: {thought}\nAction: {json.dumps(actions)}"
                
                segment_data = {
                "messages": [
                    {
                        "role": "user",
                        "content": f'''You are an assistant trained to navigate the mobile phone. 
Given a task instruction, a screen observation, and an action history sequence, 
output the next action and wait for the next observation. 
Here is the action space:

1. `INPUT`: Type a string into an element, value is not applicable and the position [x,y] is required. 
2. `SWIPE`: Swipe the screen, value is not applicable and the position [[x1,y1], [x2,y2]] is the start and end position of the swipe operation.
3. `TAP`: Tap on an element, value is not applicable and the position [x,y] is required.
4. `LONG_PRESS`: Long press on an element, value is the press duration and the position [x,y] is required.
5. `PRESS_HOME`: Press the home button, value and position are not applicable.
6. `PRESS_BACK`: Press the back button, value and position are not applicable.
7. `FINISH`: Submit the task regardless of whether it succeeds or fails. Value is the result of the task and position is not applicable.

Format your response as:
Thought: <your reasoning process>
Action: <the next action>

Format the action as a JSON object with the following keys:
{{"action": "ACTION_TYPE", "value": "element", "position": [x,y]}}
You can output multiple actions at once, and use JSON array to represent multiple actions.
If value or position is not applicable, set it as `None`.
Position might be [[x1,y1], [x2,y2]] if the action requires a start and end position.
Position represents the relative coordinates on the screenshot and should be scaled to a range of 0-1.
Task: {task}
<image>'''
                        },
                        {
                            "role": "assistant",
                            "content": actions
                        }
                    ],
                    "images": [image_file_path]
                }

            if "error" in action_type or "call_user" in action_type or "finished" in action_type:
                historical_actions.clear()
                historical_images.clear()
                continue

            if len(historical_actions) == 1:
                historical_actions_str2 = historical_actions[-1] if len(historical_actions) > 0 else ''
                historical_images_str2 = historical_images[-1] if len(historical_images) > 0 else ''

                segment_data["messages"][0]["content"] += f"{historical_actions_str2}<image>"
                segment_data["images"].insert(0, historical_images_str2)
            elif len(historical_actions) > 1:
                historical_actions_str1 = historical_actions[-2] if len(historical_actions) > 1 else '' 
                historical_actions_str2 = historical_actions[-1] if len(historical_actions) > 0 else ''
                historical_images_str1 = historical_images[-2] if len(historical_images) > 1 else ''
                historical_images_str2 = historical_images[-1] if len(historical_images) > 0 else ''

                segment_data["messages"][0]["content"] += f"{historical_actions_str1}<image>{historical_actions_str2}<image>"
                segment_data["images"].insert(0, historical_images_str2)
                segment_data["images"].insert(0, historical_images_str1)

            historical_actions.append(actions)
            historical_images.append(image_file_path)

            video_output_json.append(segment_data)
        else:
            if thought_file_path.endswith("_thought.txt"):
                historical_actions.clear()
                historical_images.clear()
            continue

    with open(output_json_path, "w", encoding='utf-8') as json_file:
        json.dump(video_output_json, json_file, ensure_ascii=False, indent=4)

def process_video_class(video_class, video_class_path, final_video_root, output_json_root, prompt_mapping):
    final_video_class_path = os.path.join(final_video_root, video_class)
    output_json_class_path = os.path.join(output_json_root, video_class)
    os.makedirs(output_json_class_path, exist_ok=True)

    for video_name in os.listdir(video_class_path):
        video_action_path = os.path.join(video_class_path, video_name)
        video_image_path = os.path.join(final_video_class_path, video_name)
        output_json_path = os.path.join(output_json_class_path, f"{video_name}.json")
        if os.path.exists(output_json_path):
            continue

        key = output_json_path.replace(".json", ".mp4")                        
        device_type = prompt_mapping.get(key, "")
        if device_type not in {"Desktop", "Mobile"}:
            return

        process_single_video(video_action_path, video_image_path, video_name, device_type, output_json_path)

def process_all_videos(final_action_root, final_video_root, output_json_root, prompt_mapping):
    for video_class in os.listdir(final_action_root):
        video_class_path = os.path.join(final_action_root, video_class)
        if not os.path.isdir(video_class_path):
            continue
        process_video_class(video_class, video_class_path, final_video_root, output_json_root, prompt_mapping)

if __name__ == "__main__":
    app = "word"

    final_action_root = f"actions/{app}"
    final_video_root = f"images/{app}"
    output_json_root = f"results/{app}"

    os.makedirs(output_json_root, exist_ok=True)

    json_path = f"cls/{app}_cls.json"
    with open(json_path, "r", encoding="utf-8") as json_file:
        prompt_mapping = json.load(json_file)

    process_all_videos(final_action_root, final_video_root, output_json_root, prompt_mapping)
