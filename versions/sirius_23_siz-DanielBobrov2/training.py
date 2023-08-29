import os
import cv2
import numpy as np
import os
import tensorflow as tf
from tensorflow.keras import layers, models
import cv2


def augment_dataset(folder_path):
    files = os.listdir(folder_path)
    files.sort(key=lambda a: int(a[:-4]))
    print(files)
    for i, file_name in enumerate(files):
        try:
            img = cv2.imread(f"{folder_path}/{file_name}")
            img = cv2.resize(img, (100, 100))
            cv2.imwrite(f"{folder_path}/{file_name}", img)
            if i % 4 == 1:
                img = img[::-1]
                cv2.imwrite(f"{folder_path}/{file_name}_1", img)
            elif i % 4 == 2:
                img = img[:, ::-1]
                cv2.imwrite(f"{folder_path}/{file_name}_1", img)
            elif i % 4 == 3:
                img = img[::-1]
                img = img[:, ::-1]
                cv2.imwrite(f"{folder_path}/{file_name}_1", img)
        except:
            print(i, file_name)


def load_images(folder_path, label):
    images = list()
    labels = list()
    for filename in os.listdir(folder_path):
        if filename.endswith(".png"):
            img_path = os.path.join(folder_path, filename)
            img = cv2.imread(img_path)
            img = cv2.resize(img, (224, 224))
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            images.append(img)
            labels.append(int(label))
    return np.array(images), np.array(labels)


def create_model():
    model = models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(128, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
    return model


incorrect = "gloves/correct/"
correct = "gloves/incorrect/"

augment_dataset(correct)
augment_dataset(incorrect)

class1_images, class1_labels = load_images(correct, 1)
class2_images, class2_labels = load_images(incorrect, 0)

images = np.concatenate((class1_images, class2_images), axis=0)
labels = np.concatenate((class1_labels, class2_labels), axis=0)

images = images / 255.0

model = create_model()

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
model.fit(images, labels, epochs=1, batch_size=32)

model.save("1_epoch__32_batch_gloves.h5")
