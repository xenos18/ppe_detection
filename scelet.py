import cv2
import torch
from torchvision import transforms
import numpy as np
import matplotlib.pyplot as plt

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import non_max_suppression_kpt, xywh2xyxy
from utils.plots import output_to_keypoint, plot_skeleton_kpts, plot_one_box

IMG_NAME = "test.png"
orig_img = cv2.imread(IMG_NAME)

# set gpu device if possible
print(torch.cuda.is_available())
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)
model = attempt_load('weights/yolov7-w6-pose.pt', map_location=device)
model.eval()


def find(orig_img, is_show_image=False):
    def show_image():
        while True:
            cv2.imshow("Video Capture", img)
            cv2.waitKey(1)

    def get_cords(kpts):
        cords = list()
        steps = 3
        palette = np.array([[255, 128, 0], [255, 153, 51], [255, 178, 102],
                            [230, 230, 0], [255, 153, 255], [153, 204, 255],
                            [255, 102, 255], [255, 51, 255], [102, 178, 255],
                            [51, 153, 255], [255, 153, 153], [255, 102, 102],
                            [255, 51, 51], [153, 255, 153], [102, 255, 102],
                            [51, 255, 51], [0, 255, 0], [0, 0, 255], [255, 0, 0],
                            [255, 255, 255]])

        pose_kpt_color = palette[[16, 16, 16, 16, 16, 0, 0, 0, 0, 0, 0, 9, 9, 9, 9, 9, 9]]
        radius = 5
        num_kpts = len(kpts) // steps

        for kid in range(num_kpts):
            r, g, b = pose_kpt_color[kid]
            x_coord, y_coord = kpts[steps * kid], kpts[steps * kid + 1]
            if not (x_coord % 640 == 0 or y_coord % 640 == 0):
                if steps == 3:
                    conf = kpts[steps * kid + 2]
                    if conf < 0.5:
                        continue
                # cv2.circle(im, (int(x_coord), int(y_coord)), radius, (int(r), int(g), int(b)), -1)
                # print(x_coord, y_coord, conf)
                cords.append([x_coord, y_coord, conf])
        return cords

    # orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)

    # resize and pad
    img = letterbox(orig_img, 640 * 3, stride=64, auto=True)[0]

    # transform to tensor
    img_ = transforms.ToTensor()(img)
    # add dimension
    img_ = torch.unsqueeze(img_, 0)
    # send the picture to the calculating device
    img_ = img_.to(device).float()

    with torch.no_grad():
        pred, _ = model(img_)

    pred = non_max_suppression_kpt(pred,
                                   conf_thres=0.25,
                                   iou_thres=0.65,
                                   nc=model.yaml['nc'],
                                   nkpt=model.yaml['nkpt'],
                                   kpt_label=True)

    peoples = list()

    def plot_pose_prediction(img: cv2.Mat, pred: list, thickness=2,
                             show_bbox: bool = True) -> cv2.Mat:
        bbox = xywh2xyxy(pred[:, 2:6])
        for idx in range(pred.shape[0]):
            plot_skeleton_kpts(img, pred[idx, 7:].T, 3)
            cords = get_cords(pred[idx, 7:].T)
            print(len(cords))

            if len(cords) > 16:
                peoples.append(cords)
            if show_bbox:
                plot_one_box(bbox[idx], img, line_thickness=thickness)

    pred = output_to_keypoint(pred)
    print([len(i) for i in pred])
    plot_pose_prediction(img, pred, show_bbox=False)

    # print(peoples, sep="\n")
    # print("\n\n")

    def dot(x, y, size=1):
        # plot_one_box([int(x), int(y), int(x) + size, int(y) + size], img, line_thickness=2)
        cv2.circle(img, [x, y], size, [255, 0, 0], thickness=size)

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

    check_left_hand()
    check_right_hand()
    if is_show_image:
        show_image()
    return img


if __name__ == "__main__":
    find(orig_img, is_show_image=True)
