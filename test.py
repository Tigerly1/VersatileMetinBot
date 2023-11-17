from PIL import Image
import cv2
import numpy as np
# Load the uploaded image

image_path = r'C:\Users\Filip\Downloads\bigCircle.png'
image = Image.open(image_path)
image_np = np.array(image)

# The target color and tolerance
target_color = np.array([82, 36, 19])
tolerance = 3


# Adjusting the filter_pixels function to ignore the alpha channel if present
def filter_pixels_ignore_alpha(image, target_color, tolerance):
    # If the image has an alpha channel, ignore it
    if image.shape[2] == 4:
        image = image[:, :, :3]

    # Calculate the difference from the target color
    diff = np.abs(image - target_color)

    # Check if the pixel is within the tolerance range for all three color channels
    mask = np.all(diff <= tolerance, axis=2)

    return mask

# Applying the adjusted filter function
mask = filter_pixels_ignore_alpha(image_np, target_color, tolerance)

# Finding the center of the remaining pixels
y_indices, x_indices = np.where(mask)
if len(y_indices) > 0 and len(x_indices) > 0:
    center_y = np.mean(y_indices)
    center_x = np.mean(x_indices)
else:
    center_y, center_x = None, None

center_coordinates = (center_x, center_y) if center_x is not None and center_y is not None else "No matching pixels found"

center_coordinates, mask.sum()  # Also returning the number of pixels that matched the filter criteria

print(center_coordinates)
# # Use the function
# center = show_top_5_circles(r"C:\Users\Filip\Downloads\bigCircle.png")
# if center:
#     print("Center of the largest circle is at:", center)
# else:
#     print("No circles found")