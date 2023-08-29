import tensorflow as tf
import cv2
import numpy as np
import os

# Загрузка модели
loaded_model_gloves = tf.keras.models.load_model("1_epoch__32_batch_gloves.h5")
loaded_model_shoes = tf.keras.models.load_model("1_epoch__32_batch_shoes.h5")


# Классификация изображения с использованием загруженной модели
def classify_gloves(img):
    img = cv2.resize(img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)
    img = img / 255.0
    prediction = loaded_model_gloves.predict(img)
    if prediction[0] < 0.5:
        return 0
    else:
        return 1


# Классификация изображения с использованием загруженной модели
def classify_shoes(img):
    img = cv2.resize(img, (224, 224))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = np.expand_dims(img, axis=0)
    img = img / 255.0
    prediction = loaded_model_shoes.predict(img)
    if prediction[0] < 0.5:
        return 0
    else:
        return 1


if __name__ == "__main__":
    folder_path = "gloves/test/"
    files = os.listdir(folder_path)
    files.sort(key=lambda a: int(a[:-4]))
    classes = list()
    for i, file_name in enumerate(files):
        try:
            image_path = f"{folder_path}/{file_name}"
            img = cv2.imread(image_path)
            classes.append(classify_gloves(img))
        except:
            print(i, file_name)
    print(*enumerate(classes), sep="\n")
    img = cv2.imread("img.png")
    print()
    print(classify_gloves(img))
