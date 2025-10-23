import cv2


def grayscale_image_func(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image[:] = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    return image


def gaussian_blur_func(image, k_size: int):
    gaussian = cv2.GaussianBlur(image, (k_size, k_size), cv2.BORDER_DEFAULT)
    image[:] = gaussian
    return image


def zoom_in_func(image):
    scale_factor = 1.2
    zoomed_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    image[:] = zoomed_image
    return image

def zoom_out_func(image):
    scale_factor = 0.8
    zoomed_image = cv2.resize(image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
    image[:] = zoomed_image
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