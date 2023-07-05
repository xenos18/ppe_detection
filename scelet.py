import cv2

from utils.datasets import letterbox
from utils.general import xywh2xyxy
from utils.plots import plot_one_box


def get_cords(kpts):
    cords = list()
    steps = 3
    num_kpts = len(kpts) // steps

    for kid in range(num_kpts):
        x_coord, y_coord = kpts[steps * kid], kpts[steps * kid + 1]
        if not (x_coord % 640 == 0 or y_coord % 640 == 0):
            if steps == 3:
                conf = kpts[steps * kid + 2]
                if conf < 0.5:
                    continue
            cords.append([x_coord, y_coord, conf])
    return cords


def show_image():
    global img
    while True:
        cv2.imshow("Video Capture", img)
        cv2.waitKey(1)


def plot_pose_prediction(img: cv2.Mat, pred: list, thickness=2,
                         show_bbox: bool = True) -> cv2.Mat:
    bbox = xywh2xyxy(pred[:, 2:6])
    for idx in range(pred.shape[0]):
        cords = get_cords(pred[idx, 7:].T)

        if len(cords) > 16:
            peoples.append(cords)
        if show_bbox:
            plot_one_box(bbox[idx], img, line_thickness=thickness)


def check_hand(elbow, hand):
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
    if interesting_pixel / pixel_count > .1:
        plot_one_box(box_cords, img, color=[0, 0, 255], line_thickness=1)
        cv2.putText(img, "Warning!", [box_cords[0], box_cords[3] + 10], 0, .5, [0, 0, 255])
    else:
        plot_one_box(box_cords, img, color=[0, 255, 0], line_thickness=1)
        cv2.putText(img, "Ok!", [box_cords[0], box_cords[3] + 10], 0, .5, [0, 255, 0])


def check_left_hand():
    for people in peoples:
        left_elbow = people[-10]
        left_hand = people[-8]
        check_hand(elbow=left_elbow, hand=left_hand)


def check_right_hand():
    for people in peoples:
        right_elbow = people[-9]
        right_hand = people[-7]
        check_hand(elbow=right_elbow, hand=right_hand)


def find(orig_img, pred, is_show_image=False):
    global img, peoples
    img = orig_img

    img = letterbox(orig_img, orig_img.shape[1], stride=64, auto=True)[0]

    peoples = list()

    plot_pose_prediction(img, pred, show_bbox=False)

    check_left_hand()
    check_right_hand()
    if is_show_image:
        show_image()
    return img
