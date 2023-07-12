import mlflow
from ultralytics import YOLO
import os
from dotenv import load_dotenv
load_dotenv()

# Проверить наличие переменной окружения cо строкой подключения MLflow
if 'MLFLOW_TRACKING_URI' not in os.environ:
    raise Exception("Variable MLFLOW_TRACKING_URI is not found :(")

experiment_name = "siz-object-detection"
run_name = "run-1"
epochs_count = 30

model = YOLO("yolov8n.pt")
model.train(data="data.yaml", epochs=epochs_count, project=experiment_name, name=run_name)

mlflow.log_artifact(__file__)
mlflow.log_artifact('data.yaml')
mlflow.log_artifact('datasets.zip')
# Добавить что-то свое
mlflow.end_run()
