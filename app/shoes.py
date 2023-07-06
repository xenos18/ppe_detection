from yolov7 import *
from typing import Any


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "{" + str(self.x) + "; " + str(self.y) + "}"


class ShoesLos:
    def get_cords(self, kpts) -> list[list[Any]]:
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

    def plot_pose_prediction(self, pred: list, thickness=2, show_bbox: bool = True) -> list[list[list[Any]]]:
        bbox = xywh2xyxy(pred[:, 2:6])
        peoples = list()
        for idx in range(pred.shape[0]):
            cords = self.get_cords(pred[idx, 7:].T)
            if len(cords) > 16:
                peoples.append(cords)
            if show_bbox:
                plot_one_box(bbox[idx], self.img, line_thickness=thickness)
        return peoples

    def check_hand(self, elbow, hand):
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
                pixel = [i for i in self.img[x, y]]
                # pixel = self.img[x, y]
                for i in range(len(pixel)):
                    pixel[i] = pixel[i] // round_val * round_val
                pixel_count += 1
                if pixel[0] == 50 and pixel[1] == 0 and pixel[2] == 0 \
                        or pixel[0] == 50 and pixel[1] == 50 and pixel[2] == 50:
                    interesting_pixel += 1
        prediction = True if interesting_pixel / pixel_count > .1 else False
        coords = [box_cords[0], box_cords[1], box_cords[2], box_cords[3], prediction]
        return coords

    def check_left_hand(self, boxes: list):
        for people in self.peoples:
            left_elbow = people[-4]
            left_hand = people[-2]
            boxes.append(self.check_hand(elbow=left_elbow, hand=left_hand))
        return boxes

    def check_right_hand(self, boxes):
        for people in self.peoples:
            right_elbow = people[-3]
            right_hand = people[-1]
            boxes.append(self.check_hand(elbow=right_elbow, hand=right_hand))
        return boxes

    def check_hands(self):
        boxes = list()
        boxes = self.check_left_hand(boxes)
        boxes = self.check_right_hand(boxes)
        return boxes

    def find(self, orig_img, pred):
        self.img = letterbox(orig_img, orig_img.shape[1], stride=64, auto=True)[0]
        self.peoples = self.plot_pose_prediction(pred, show_bbox=False)
        return self.check_hands()
