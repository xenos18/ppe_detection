import random

import cv2
import math
from deepface import DeepFace
from database.connect import *
import os
import shutil

if os.path.exists("faces/compiled"):
    shutil.rmtree("faces/compiled")
os.mkdir("faces/compiled")

with Session(engine) as session:
    q = select(User)
    for user in session.scalars(q):
        for img in os.listdir(f"faces/{user.face_folder}"):
            rnd = hex((user.id << 128) + random.randint(0, (1 << 128) - 1))
            image = cv2.imread(f"faces/{user.face_folder}/{img}")

            cv2.imwrite(f"faces/compiled/{rnd}.jpg", image)


print(DeepFace.find(f"faces/compiled/{os.listdir('faces/compiled')[0]}", "faces/compiled", enforce_detection=False))
