import cv2
import numpy as np


def rectangle_func(image, pt1: float, pt2: float):
    image = cv2.rectangle(image, pt1, pt2, (0, 0, 0))
    return image


def circle_func(image, pt1: float):
    image = cv2.circle(image, pt1, 10, (0, 0, 0))
    return image


def polygon_func(image, array: []):
    for i in range(len(list)):
        array.append(i)

    image = cv2.polylines(image, array, True, (0, 0, 0))
    return image


def ellipse_func(image, pt1: float):
    image = cv2.ellipse(image, pt1, (150, 75), 45,
                        0, 360, (0, 0, 0), 2)
    return image


def line_func(image, pt1: float, pt2: float):
    image = cv2.line(image, pt1, pt2, (0, 0, 0))
    return image

