from PIL import Image, ImageDraw, ImageFont

image = Image.open("data/temp/bd72f23834bb19ef605994a2497bd28286893a5d.jpg")
'''
from dinox
{'code': 0, 'msg': 'ok', 'data': {'error': None, 'result': {'objects': [{'bbox': [409.5694274902344, 44.03757858276367, 470.7210693359375, 115.76675415039062], 'category': 'red box', 'hand': None, 'mask': {'counts': 'gkf07Z?b1aN1N101O000O010001N100000000000000000000001O000000000000000000000000000000000000001OO10000000000001O00000000000000000000000000000001N1O5[OVBoN', 'size': [1111, 500]}, 'pose': None, 'score': 0.351311057806015}]}, 'session_id': '034122526abc4ea8830a40b2fe2e11c0', 'status': 'success', 'uuid': 'ff4afbd8-7a33-401e-8ff9-6cb2ebb4d570'}}

from groundingdino v1.5
success resp: {'code': 0, 'msg': 'ok', 'data': {'error': None, 'result': {'mask_url': None, 'objects': [{'bbox': [409.0737609863281, 43.42134475708008, 470.32476806640625, 115.21572875976562], 'category': 'red box', 'score': 0.47227349877357483}]}, 'session_id': '4dc4cabb00084d2f8c9eaa980caff89a', 'status': 'success', 'uuid': '34a28b9c-cb8d-427b-b4a7-a440af4f2548'}}
'''
# draw bounding box on image
models = ["DinoX", "GroundingDINO"]
for i, bbox in enumerate([[409.5694274902344, 44.03757858276367, 470.7210693359375, 115.76675415039062], [409.0737609863281, 43.42134475708008, 470.32476806640625, 115.21572875976562]]):
    draw = ImageDraw.Draw(image)
    draw.rectangle(bbox, outline='blue')
    # add text category make it larger
    draw.text((bbox[0], bbox[1]), f"red box ({models[i]})", fill='blue', font=ImageFont.truetype("arial.ttf", 20))
image.show()
