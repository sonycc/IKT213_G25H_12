import cv2


def rotate_image_func(image, angle: int):

    if angle not in [90, 180, 270]:
        raise ValueError("Angle must be 90, 180, or 270 degrees")

    if angle == 90:
        return cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(image, cv2.ROTATE_180)
    else:  # 270
        return cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)


def crop_image_func(image, x1: int, y1: int, x2: int, y2: int):

    h, w = image.shape[:2]
    if not (0 <= x1 < x2 <= w) or not (0 <= y1 < y2 <= h):
        raise ValueError("Crop coordinates out of bounds")

    cropped_image = image[y1:y2, x1:x2].copy()
    return cropped_image


def resize_func(image, x1: int, y1: int, x2: int, y2: int):
    width = max(x2 - x1, 1)
    height = max(y2 - y1, 1)
    resized_image = cv2.resize(image, (width, height), interpolation=cv2.INTER_LINEAR)
    return resized_image


def flip_horizontal_func(image):
    image[:] = cv2.flip(image, 1)
    return image


def flip_vertical_func(image):
    image[:] = cv2.flip(image, 0)
    return image
