import cv2
import numpy as np


def rectangle_func(image, x1: int, y1: int, x2: int, y2: int):
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 0))
    return image


def circle_func(image, x1: int, y1: int):
    cv2.circle(image, (x1, y1), 10, (0, 0, 0))
    return image


def polygon_func(image, array: []):
    for i in range(len(array)):
        array.append(i)

    cv2.polylines(image, array, True, (0, 0, 0))
    return image


def ellipse_func(image, x1: int, y1: int):
    cv2.ellipse(image, (x1, y1), (150, 75), 45,
                        0, 360, (0, 0, 0), 2)
    return image


def line_func(image, x1: int, y1: int, x2: int, y2: int):
    cv2.line(image, (x1, y1), (x2, y2), (0, 0, 0))
    return image

