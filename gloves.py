from typing import Any

import cv2
import torch
from torchvision import transforms

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import non_max_suppression_kpt, xywh2xyxy
from utils.plots import output_to_keypoint, plot_skeleton_kpts, plot_one_box
from neural_networks import classify_gloves, classify_shoes


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

    def __repr__(self):
        return "Box(" + str(self.left_top) + ", " + str(self.right_bottom) + ", " + str(self.is_ok) + ")"

    def __str__(self):
        return "[" + str(self.left_top) + ", " + str(self.right_bottom) + ", " + str(self.is_ok) + "]"


class Dima:
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

    def get_box_cords(self, elbow, hand):
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
        return box_cords

    def check_left_hand(self) -> list[Box]:
        for people in self.peoples:
            left_elbow = people[-10]
            left_hand = people[-8]
            self.boxes.append(self.check_hand(elbow=left_elbow, hand=left_hand))
        return boxes

    def check_right_hand(self) -> list[Box]:
        for people in self.peoples:
            right_elbow = people[-9]
            right_hand = people[-7]
            self.boxes.append(self.check_hand(elbow=right_elbow, hand=right_hand))
        return boxes

    def check_peoples(self):
        for people in self.peoples:
            left_elbow = people[-10]
            left_hand = people[-8]
            box_cords = self.get_box_cords(left_elbow, left_hand)
            prediction = classify_gloves(self.img[box_cords[1]:box_cords[3], box_cords[0]:box_cords[2]])
            self.boxes.append(Box(Dot(box_cords[0], box_cords[1]), Dot(box_cords[2], box_cords[3]), prediction))

            right_elbow = people[-9]
            right_hand = people[-7]
            box_cords = self.get_box_cords(right_elbow, right_hand)
            prediction = classify_gloves(self.img[box_cords[1]:box_cords[3], box_cords[0]:box_cords[2]])
            self.boxes.append(Box(Dot(box_cords[0], box_cords[1]), Dot(box_cords[2], box_cords[3]), prediction))

            left_elbow_shoe = people[-4]
            left_hand_shoe = people[-2]
            box_cords = self.get_box_cords(left_elbow_shoe, left_hand_shoe)
            prediction = classify_shoes(self.img[box_cords[1]:box_cords[3], box_cords[0]:box_cords[2]])
            self.boxes.append(Box(Dot(box_cords[0], box_cords[1]), Dot(box_cords[2], box_cords[3]), prediction))

            right_hand_shoe = people[-1]
            right_elbow_shoe = people[-3]
            box_cords = self.get_box_cords(right_elbow_shoe, right_hand_shoe)
            prediction = classify_shoes(self.img[box_cords[1]:box_cords[3], box_cords[0]:box_cords[2]])
            self.boxes.append(Box(Dot(box_cords[0], box_cords[1]), Dot(box_cords[2], box_cords[3]), prediction))
        return self.boxes

    def check_hands(self) -> list[Box]:
        self.check_left_hand()
        self.check_right_hand()
        return self.boxes

    def find(self, orig_img, pred) -> list[Box]:
        self.boxes = list()
        self.img = letterbox(orig_img, orig_img.shape[1], stride=64, auto=True)[0]
        self.peoples = self.plot_pose_prediction(pred, show_bbox=False)
        return self.check_peoples()


if __name__ == "__main__":
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    model = attempt_load('weights/yolov7-w6-pose.pt', map_location=device)
    model.eval()

    orig_img = cv2.imread('test2.png')
    img = letterbox(orig_img, orig_img.shape[1], stride=64, auto=True)[0]

    img_ = transforms.ToTensor()(img)
    img_ = torch.unsqueeze(img_, 0)
    img_ = img_.to(device).float()

    with torch.no_grad():
        pred, _ = model(img_)

    pred = non_max_suppression_kpt(pred,
                                   conf_thres=0.25,
                                   iou_thres=0.65,
                                   nc=model.yaml['nc'],
                                   nkpt=model.yaml['nkpt'],
                                   kpt_label=True)


    def plot_pose_prediction1(img: cv2.Mat, pred: list, thickness=2,
                              show_bbox: bool = True) -> cv2.Mat:
        bbox = xywh2xyxy(pred[:, 2:6])
        for idx in range(pred.shape[0]):
            plot_skeleton_kpts(img, pred[idx, 7:].T, 3)
            if show_bbox:
                plot_one_box(bbox[idx], img, line_thickness=thickness)


    pred = output_to_keypoint(pred)
    shit = Dima()
    boxes = shit.find(img, pred)

    print(boxes)
    for box in boxes:
        color = [0, 255, 0] if box.is_ok else [0, 0, 255]
        plot_one_box([box.left_top.x, box.left_top.y, box.right_bottom.x, box.right_bottom.y], img, color,
                     line_thickness=3)
        # cv2.putText(img, str(box.is_ok), [box.left_top.x, box.right_bottom.y + 15], 1, 1, color)

    # plot_pose_prediction1(img, pred)
    while True:
        cv2.imshow("img", img)
        cv2.waitKey(1)
