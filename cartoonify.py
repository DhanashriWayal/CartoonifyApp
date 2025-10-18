import cv2
import numpy as np
from PIL import Image

def adjust_brightness_contrast(img, brightness=0, contrast=0):
    """Adjust brightness and contrast"""
    brightness = int((brightness - 50) * 2.55)
    contrast = int((contrast - 50) * 2.55)
    buf = np.int16(img)
    buf = buf * (contrast / 127 + 1) - contrast + brightness
    buf = np.clip(buf, 0, 255)
    return np.uint8(buf)

def comic_effect(img):
    """Create strong comic-book style effect"""
    # Convert to grayscale and blur slightly
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)

    # Detect bold edges using Canny
    edges = cv2.Canny(gray, threshold1=80, threshold2=180)
    edges = cv2.dilate(edges, None)  # thicken lines
    edges = 255 - edges  # invert for white background

    # Reduce colors (posterize)
    data = np.float32(img).reshape((-1, 3))
    K = 5  # fewer clusters = more comic look
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
    _, label, center = cv2.kmeans(data, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    center = np.uint8(center)
    reduced = center[label.flatten()].reshape(img.shape)

    # Increase saturation for comic punch
    hsv = cv2.cvtColor(reduced, cv2.COLOR_BGR2HSV)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.4, 0, 255)
    comic = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # Overlay dark edges
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    comic_final = cv2.bitwise_and(comic, edges_colored)

    return comic_final

def cartoonify_image(image: Image.Image, brightness=50, contrast=50, grayscale_strength=50,
                     edge_strength=9, color_smooth=9, style="Classic"):
    # Convert PIL → OpenCV
    img = np.array(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Adjust brightness & contrast
    img = adjust_brightness_contrast(img, brightness, contrast)

    # === Different Styles ===
    if style == "Comic":
        cartoon = comic_effect(img)

    else:
        # Default cartoonify process
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.medianBlur(gray, 7)
        edges = cv2.adaptiveThreshold(gray, 255,
                                      cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY,
                                      9 if edge_strength < 9 else edge_strength | 1, 9)
        color = cv2.bilateralFilter(img, d=9, sigmaColor=300, sigmaSpace=color_smooth * 10)
        data = np.float32(color).reshape((-1, 3))
        K = 6
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.001)
        _, label, center = cv2.kmeans(data, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        center = np.uint8(center)
        result = center[label.flatten()].reshape(color.shape)
        cartoon = cv2.bitwise_and(result, result, mask=edges)

        # Optional grayscale blend
        if grayscale_strength < 100:
            alpha = grayscale_strength / 100
            cartoon = cv2.addWeighted(cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR),
                                      alpha, cartoon, 1 - alpha, 0)

        # Soft / Pencil / Classic variations
        if style == "Pencil":
            gray_blur = cv2.GaussianBlur(gray, (21, 21), 0)
            sketch = cv2.divide(gray, gray_blur, scale=256)
            cartoon = cv2.cvtColor(sketch, cv2.COLOR_GRAY2RGB)
        elif style == "Soft":
            cartoon = cv2.bilateralFilter(cartoon, 9, 150, 150)

    # Convert back to RGB
    cartoon_rgb = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
    return cartoon_rgb
