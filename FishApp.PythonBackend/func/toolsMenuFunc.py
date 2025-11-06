import cv2


def grayscale_image_func(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image[:] = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return image


def gaussian_blur_func(image, k_size: int):
    gaussian = cv2.GaussianBlur(image, (k_size, k_size), cv2.BORDER_DEFAULT)
    image[:] = gaussian
    return image


def sobel_func(image, k_size: int):
    image = grayscale_image_func(image)
    gaussian = gaussian_blur_func(image, k_size)

    sobel_x = cv2.Sobel(gaussian, cv2.CV_64F, 1, 0, 1)
    sobel_y = cv2.Sobel(gaussian, cv2.CV_64F, 0, 1, 1)
    image_sobel_magnitude = cv2.magnitude(sobel_x, sobel_y)
    image_sobel_magnitude = cv2.convertScaleAbs(image_sobel_magnitude)
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


def textbox_func(image, pt1: float, pt2: float, text: str):
    image = cv2.putText(image, text, (pt1, pt2), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    return image
