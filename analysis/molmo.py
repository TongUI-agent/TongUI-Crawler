from PIL import Image
import numpy as np  

''' output
<points x1="3.0" y1="69.5" x2="3.1" y2="80.6" x3="6.9" y3="69.5" x4="7.0" y4="80.6" x5="11.5" y5="69.5" x6="11.5" y6="80.6" x7="15.2" y7="69.5" x8="15.2" y8="80.6" x9="18.9" y9="69.5" x10="19.0" y10="80.6" x11="22.7" y11="69.5" x12="22.7" y12="80.6" alt="one corner of each red rectangle">one corner of each red rectangle</points>
'''


img = Image.open("data/example1.jpeg")
# Get image dimensions
width, height = img.size
print("Image size:", width, height)
# Original reference dimensions
ref_size = 100

# draw point based on the points in the output
points = [(3.0, 69.5), (3.1, 80.6), (6.9, 69.5), (7.0, 80.6), (11.5, 69.5), (11.5, 80.6), (15.2, 69.5), (15.2, 80.6), (18.9, 69.5), (19.0, 80.6), (22.7, 69.5), (22.7, 80.6)]

# selected points based on color red
selected_points = set()
for point in points:
    scaled_x = int(point[0] * width / ref_size)
    # Flip and scale y-coordinate
    scaled_y = int(point[1] * height / ref_size)
    rgb = img.getpixel((scaled_x, scaled_y))
    ref_color = (255, 0, 0, 255)
    dist = np.sum(np.abs(np.array(rgb) - np.array(ref_color)))
    if dist < 100:
        selected_points.add(point)
print(selected_points)
for point in selected_points:
    # Scale coordinates according to actual image size
    scaled_x = int(point[0] * width / ref_size)
    # Flip and scale y-coordinate
    scaled_y = int(point[1] * height / ref_size)
    rgb = img.getpixel((scaled_x, scaled_y))
    # Draw a larger point (3x3 pixels)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            x, y = scaled_x + dx, scaled_y + dy
            if 0 <= x < width and 0 <= y < height:
                if (x, y) not in selected_points:
                    img.putpixel((x, y), (0, 255, 0))
                else:
                    img.putpixel((x, y), (0, 0, 255))
    # Get RGB value at the center point
    
    print(f"RGB value at point ({scaled_x}, {scaled_y}): {rgb}")
img.show()
