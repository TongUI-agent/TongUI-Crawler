from bs4 import BeautifulSoup

white_list = [
    "方法/步骤",
]

def parse_section(section):
    steps = []
    # Find all step items
    step_items = section.find_all('li', class_='exp-content-list')
    # print("Step items:", len(step_items))
    for item in step_items:
        step_dict = {}
        
        # Get step text
        step_text = item.find('div', class_='content-list-text')
        if step_text:
            step_dict['text'] = step_text.text.strip()
        
        # Get step image if exists
        step_image = item.find("img", class_="exp-image-default")
        # print("step image", step_image)
        
        # if step_image:
        #     print(step_image.attrs.keys())
        if step_image and 'src' in step_image.attrs:
            step_dict['image_url'] = step_image['src']
        elif step_image and 'data-src' in step_image.attrs:
            step_dict['image_url'] = step_image['data-src']
        steps.append(step_dict)
    return steps
def parse_baidu_jingyan(html):
    soup = BeautifulSoup(html, 'html.parser')
    # print("Preview HTML", html[:1000])
    # Find the 方法/步骤 section
    sections = soup.find_all('div', class_='exp-content-block')
    # print("Steps section:", len(sections))
    if sections:
        steps = []
        # filter by section title
        section_id_selected = None
        for section_id, section in enumerate(sections):
            section_title = section.find('h2', class_='exp-content-head')
            if section_title is None:
                continue
            # print("section title", section_title)
            for keyword in white_list:
                if keyword in section_title.text.strip():
                    section_id_selected = section_id
                    break
        if section_id_selected is None:
            for section in sections:
                # filter by section title
                # print(section)
                steps.extend(parse_section(section))
        else:
            steps = parse_section(sections[section_id_selected])
        return steps
    
    return None

if __name__ == "__main__":
    with open("html.html", "r") as file:
        html = file.read()
        print(parse_baidu_jingyan(html))