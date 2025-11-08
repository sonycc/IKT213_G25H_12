import cv2
import numpy as np

current_zoom = 1.0

def grayscale_image_func(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image[:] = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return image


def gaussian_blur_func(image, k_size: int):
    gaussian = cv2.GaussianBlur(image, (k_size, k_size), cv2.BORDER_DEFAULT)
    image[:] = gaussian
    return image


def sobel_func(image, k_size: int):
    gray = grayscale_image_func(image)
    gaussian = gaussian_blur_func(gray, k_size)

    sobel_x = cv2.Sobel(gaussian, cv2.CV_64F, 1, 0, ksize=k_size)
    sobel_y = cv2.Sobel(gaussian, cv2.CV_64F, 0, 1, ksize=k_size)
    image_sobel_magnitude = cv2.magnitude(sobel_x, sobel_y)
    image_sobel_magnitude = cv2.convertScaleAbs(image_sobel_magnitude)

    if len(image.shape) == 3 and image.shape[2] == 3:
        image_sobel_magnitude = cv2.cvtColor(image_sobel_magnitude, cv2.COLOR_GRAY2BGR)

    image[:] = image_sobel_magnitude
    return image


def binary_filter_func(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    if gray.dtype != "uint8":
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX).astype("uint8")

    # optional / can improve quality
    gray_blur = cv2.GaussianBlur(gray, (5, 5), 0)

    binary = cv2.adaptiveThreshold(
        gray_blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        # For finer detail: lower blockSize (must be odd), For smoother global effect: increase it
        # for C: if too bright of dark, increase or reduce
        21, 5
    )

    binary_bgr = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
    image[:] = binary_bgr
    return image


def textbox_func(image, x1: int, y1: int, x2: int, y2: int, text: str):
    font = cv2.FONT_HERSHEY_SIMPLEX
    overlay = image.copy()

    cv2.rectangle(overlay, (x1, y1), (x2, y2), (255, 255, 255), -1)
    cv2.addWeighted(overlay, 0.5, image, 0.5, 0, image)

    cv2.putText(image, text, (x1 + 10, y2 - 20), font, 1, (0, 0, 0), 2)

    return image


def color_picker_func(image, x1: int, y1: int):
    b, g, r = image[y1, x1]
    return int(r), int(g), int(b)

zoomed = 0

def zoom_in_func(image):
    global zoomed
    zoom_factor = 1.2
    height, width = image.shape[:2]

    new_height = int(height / zoom_factor)
    new_width = int(width / zoom_factor)

    start_x = (width - new_width) // 2
    start_y = (height - new_height) // 2

    cropped_image = image[start_y: start_y + new_height, start_x: start_x + new_width]

    zoomed_image = cv2.resize(cropped_image, (width, height), interpolation=cv2.INTER_LINEAR)
    zoomed += 1
    return zoomed_image



