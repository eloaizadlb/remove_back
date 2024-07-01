import cv2
import numpy as np
from PIL import Image, UnidentifiedImageError
import io
import base64

def create_center_focus_mask(shape, center_weight=1.0, edge_weight=0.1):
    rows, cols = shape
    mask = np.zeros((rows, cols), dtype=np.float32)

    for i in range(rows):
        for j in range(cols):
            distance_to_center = np.sqrt((i - rows / 2) ** 2 + (j - cols / 2) ** 2)
            max_distance = np.sqrt((rows / 2) ** 2 + (cols / 2) ** 2)
            weight = edge_weight + (center_weight - edge_weight) * (1 - distance_to_center / max_distance)
            mask[i, j] = weight

    return mask

def remove_background(image_base64):
    try:
        # Remove the data URL prefix if it exists
        if image_base64.startswith("data:image"):
            image_base64 = image_base64.split(",")[1]

        # Decode the base64 image
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data)).convert("RGBA")
    except (base64.binascii.Error, UnidentifiedImageError) as e:
        raise ValueError("Invalid image data")

    image = np.array(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGRA)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce image noise and improve contour detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Apply Otsu's thresholding
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Apply Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Combine binary and edges
    combined = cv2.bitwise_or(binary, edges)

    # Create center focus mask and apply it to the combined image
    center_focus_mask = create_center_focus_mask(combined.shape)
    weighted_combined = cv2.multiply(combined.astype(np.float32), center_focus_mask)
    weighted_combined = cv2.normalize(weighted_combined, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Find contours
    contours, _ = cv2.findContours(weighted_combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create an empty mask
    mask = np.zeros_like(gray)

    # Fill the mask with the contours
    for contour in contours:
        cv2.drawContours(mask, [contour], -1, (255), thickness=cv2.FILLED)

    # Ensure that only external contours are filled
    mask = cv2.bitwise_and(binary, mask)

    # Bitwise-and the mask with the original image
    result = cv2.bitwise_and(image, image, mask=mask)

    # Convert the result to RGBA (adding an alpha channel)
    b, g, r, a = cv2.split(result)
    rgba = cv2.merge((b, g, r, a))

    # Convert the result to PIL image and then to base64
    result_image = Image.fromarray(cv2.cvtColor(rgba, cv2.COLOR_BGRA2RGBA))
    buffered = io.BytesIO()
    result_image.save(buffered, format="PNG")
    result_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return result_base64
