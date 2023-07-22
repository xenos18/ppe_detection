from processing import Model
import json
import cv2

if __name__ == '__main__':
    with open('sequence/seq.json') as file:
        seq = json.load(file)["sequence"]
    model = Model(seq)
    capture = cv2.VideoCapture(0)
    while True:
        ret, frame = capture.read()
        if not ret:
            break
        img = model.prediction(frame)
        cv2.imshow('video feed', img)
        if cv2.waitKey(10) == 27:
            break
    capture.release()
    cv2.destroyAllWindows()