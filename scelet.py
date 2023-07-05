import cv2
import torch
from torchvision import transforms
import numpy as np
import matplotlib.pyplot as plt

from models.experimental import attempt_load
from utils.datasets import letterbox
from utils.general import non_max_suppression_kpt, xywh2xyxy
from utils.plots import output_to_keypoint, plot_skeleton_kpts, plot_one_box

IMG_NAME = "test1.png"

# set gpu device if possible
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model = attempt_load('weights/yolov7-w6-pose.pt', map_location=device)
model.eval()


def show_image(img):
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


orig_img = cv2.imread(IMG_NAME)
orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)

# resize and pad
img = letterbox(orig_img, 640, stride=64, auto=True)[0]

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


def plot_pose_prediction(img: cv2.Mat, pred: list, thickness=2,
                         show_bbox: bool = True) -> cv2.Mat:
    bbox = xywh2xyxy(pred[:, 2:6])
    for idx in range(pred.shape[0]):
        plot_skeleton_kpts(img, pred[idx, 7:].T, 3)
        cords = get_cords(pred[idx, 7:].T)
        print(*cords, sep="\n")
        print(len(cords))
        if show_bbox:
            plot_one_box(bbox[idx], img, line_thickness=thickness)


pred = output_to_keypoint(pred)
plot_pose_prediction(img, pred, show_bbox=False)

show_image(img)
