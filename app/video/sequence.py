import cv2
import config
from database.models import LabEvent, ShEvent
from database.main_db import add_sh_event
import os
from pathlib import Path

class Sequence:
    last_objects = list()
    FPS_UPDARE = 10

    def __init__(self, seq_list):
        self.frame_count = 0

        self.model = config.model

        self.seq_list = seq_list
        self.yes_objects_now = list()
        self.yes_objects = list()
        self.seq_num = 0
        self.check_dict = dict()
        self.stop = False

        self.id_now = -1
        self.time_in = 0
        self.time_out = 0
        self.check_seq = False

        self.img = 0
        self.create_check_dict()

    def create_check_dict(self):
        for i in range(len(self.seq_list)):
            self.check_dict[self.seq_list[i]] = 0

    def update_check_dict(self):
        for i in range(len(self.seq_list)):
            if self.check_dict[self.seq_list[i]] != -1:
                self.check_dict[self.seq_list[i]] = 0

    def prediction(self, results):
        self.frame_count += 1
        self.yes_objects_now = list()

        img = results[0].orig_img
        classes = results[0].names
        for i in range(len(results[0].boxes.cls)):
            c = classes[int(results[0].boxes.cls[i])]
            if 'no_' not in c and c in self.seq_list:
                self.yes_objects_now.append(c)
            cv2.rectangle(
                img,
                list(map(int, results[0].boxes.xyxy[i][:2].tolist())),
                list(map(int, results[0].boxes.xyxy[i][2:].tolist())),
                (0, 0, 255) if "no_" in c else (0, 255, 0),
                4
            )

            xn, yn = map(int, results[0].boxes.xyxy[i][:2].tolist())

            cv2.putText(
                img,
                c,
                (xn, yn),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 255, 255),
                1,
                cv2.LINE_AA
            )
        self.update_sequence()
        self.img = img

    def update_sequence(self):
        for i in range(len(self.yes_objects_now)):
            if self.check_dict[self.yes_objects_now[i]] != -1:
                self.check_dict[self.yes_objects_now[i]] += 1
        if self.frame_count % self.FPS_UPDARE == 0:
            for key, value in self.check_dict.items():
                if key == 'shoe' or key == 'glove':
                    if value > (2 * self.FPS_UPDARE) // 2:
                        self.yes_objects.append(key)
                else:
                    if value > self.FPS_UPDARE // 2:
                        self.yes_objects.append(key)
            if self.frame_count == self.FPS_UPDARE:
                self.last_objects.extend(self.yes_objects)
            else:
                self.check_sequence()
                self.update_check_dict()
                self.last_objects = list()
                self.last_objects.extend(self.yes_objects)
                self.yes_objects = list()

    def check_sequence(self):
        print(f'Нужно надеть {self.seq_list[self.seq_num]}')
        for i in range(len(self.yes_objects)):
            if self.yes_objects[i] not in self.last_objects and self.stop is False and self.check_dict[self.yes_objects[i]] != -1:
                if self.yes_objects[i] == 'glove' or self.yes_objects[i] == 'shoe':
                    if self.yes_objects.count(self.yes_objects[i]) == 2:
                        print(f'Вы надели {self.yes_objects[i]}')
                else:
                    print(f'Вы надели {self.yes_objects[i]}')
                self.check_dict[self.yes_objects[i]] = 0
                if self.seq_list[self.seq_num] == self.yes_objects[i]:
                    if self.seq_num == len(self.seq_list) - 1:
                        self.check_seq = True
                        print('Вы абсолютно правильно оделись')
                    else:
                        self.seq_num += 1
                else:
                    self.check_seq = False
                    print(f'Вы неправильно одеваетесь. Нужно надеть {self.seq_list[self.seq_num]}')
                    self.stop = self.yes_objects[i]
                    self.check_dict[self.yes_objects[i]] = -2
        for i in range(len(self.last_objects)):
            if self.last_objects[i] not in self.yes_objects:
                print(f'Вы сняли {self.last_objects[i]}')
                if self.check_dict[self.last_objects[i]] == -2:
                    self.check_dict[self.last_objects[i]] = 0
                    self.stop = False
                elif self.seq_list[self.seq_num - 1] == self.last_objects[i]:
                    self.seq_num -= 1
                    self.check_dict[self.last_objects[i]] = 0

    def add_event(self):
        max_ind = 0
        
        Path('../save_frames/shluse/').mkdir(parents=True, exist_ok=True)
        for filename in os.listdir('../save_frames/shluse/'):
            ind = int(filename[:-4])
            if ind > max_ind:
                max_ind = ind
        filename = f'../save_frames/shluse/{max_ind + 1}.jpg'
        cv2.imwrite(filename, self.img)
        add_sh_event(str(self.time_in), str(self.time_out), self.check_seq, filename)

