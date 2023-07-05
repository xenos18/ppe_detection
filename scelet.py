from typing import List, Any, Type

import cv2

from utils.datasets import letterbox
from utils.general import xywh2xyxy
from utils.plots import plot_one_box


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "{" + str(self.x) + "; " + str(self.y) + "}"


class Box:
    def __init__(self, left_top: Dot, right_bottom: Dot, is_ok: bool):
        self.left_top = left_top
        self.right_bottom = right_bottom
        self.is_ok = is_ok


def get_cords(kpts) -> list[list[Any]]:
    cords = list()
    steps = 3
    num_kpts = len(kpts) // steps

    for kid in range(num_kpts):
        x_coord, y_coord = kpts[steps * kid], kpts[steps * kid + 1]
        if not (x_coord % 640 == 0 or y_coord % 640 == 0):
            conf = kpts[steps * kid + 2]
            if conf < 0.5:
                continue
            cords.append([x_coord, y_coord, conf])
    return cords


def plot_pose_prediction(img: cv2.Mat, pred: list, thickness=2, show_bbox: bool = True) -> list[list[list[Any]]]:
    bbox = xywh2xyxy(pred[:, 2:6])
    peoples = list()
    for idx in range(pred.shape[0]):
        cords = get_cords(pred[idx, 7:].T)
        if len(cords) > 16:
            peoples.append(cords)
        if show_bbox:
            plot_one_box(bbox[idx], img, line_thickness=thickness)
    return peoples


def check_hand(elbow, hand, img) -> Type[Box]:
    box_size = (
                       (elbow[0] - hand[0]) ** 2
                       +
                       (elbow[1] - hand[1]) ** 2
               ) ** 0.5 * (2 / 3)
    box_size *= 0.5
    box_pos_x = (
                        hand[0] - elbow[0]
                ) * .5
    box_pos_y = (
                        hand[1] - elbow[1]
                ) * .5
    box_cords = [
        int(hand[0] - box_size + box_pos_x), int(hand[1] - box_size + box_pos_y),
        int(hand[0] + box_size + box_pos_x), int(hand[1] + box_size + box_pos_y)
    ]

    round_val = 50

    pixel_count = 0
    interesting_pixel = 0
    for y in range(box_cords[0], box_cords[2]):
        for x in range(box_cords[1], box_cords[3]):
            pixel = [i for i in img[x, y]]
            for i in range(len(pixel)):
                pixel[i] = pixel[i] // round_val * round_val
            pixel_count += 1
            if pixel[0] == 50 and pixel[1] == 50 and pixel[2] == 100 \
                    or pixel[0] == 0 and pixel[1] == 50 and pixel[2] == 100 \
                    or pixel[0] == 100 and pixel[1] == 150 and pixel[2] == 200:
                interesting_pixel += 1
    print(interesting_pixel / pixel_count)
    prediction = False if interesting_pixel / pixel_count > .1 else True
    Box(Dot(box_cords[0], box_cords[1]),    Dot(box_cords[2], box_cords[3]), prediction)
    return Box


def check_left_hand(peoples, img, boxes: list) -> list[Box]:
    for people in peoples:
        left_elbow = people[-10]
        left_hand = people[-8]
        boxes.append(check_hand(elbow=left_elbow, hand=left_hand, img=img))
    return boxes


def check_right_hand(peoples, img, boxes) -> list[Box]:
    for people in peoples:
        right_elbow = people[-9]
        right_hand = people[-7]
        boxes.append(check_hand(elbow=right_elbow, hand=right_hand, img=img))
    return boxes


def check_hands(peoples, img) -> list[Box]:
    boxes: list[Box] = list()
    boxes = check_left_hand(peoples, img, boxes)
    boxes = check_right_hand(peoples, img, boxes)
    return boxes


def find(orig_img, pred) -> list[Box]:
    img = letterbox(orig_img, orig_img.shape[1], stride=64, auto=True)[0]
    peoples = plot_pose_prediction(img, pred, show_bbox=False)
    return check_hands(peoples, img)
