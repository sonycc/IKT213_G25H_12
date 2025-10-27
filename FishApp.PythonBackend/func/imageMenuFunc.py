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

    image[:] = image[y1:y2, x1:x2]
    return image


def flip_horizontal_func(image):
    image[:] = cv2.flip(image, 1)
    return image


def flip_vertical_func(image):
    image[:] = cv2.flip(image, 0)
    return image
