import mlflow
from dotenv import load_dotenv
from ultralytics import YOLO

load_dotenv()

experiment_name = "siz-object-detection"
run_name = "run-1"

model = YOLO("yolov8n.pt")

model.train(data="data.yaml", epochs=30, project=experiment_name, name=run_name)

# MLFLOW_PORT = os.environ['MLFLOW_PORT']

# mlflow.set_tracking_uri(f"http://localhost:{MLFLOW_PORT}")

# mlflow.set_experiment(experiment_name)

# with mlflow.start_run(run_name="experiment 3"):
    # mlflow.log_params(vars(model.trainer.model.args))
    # metrics_dict = {f"{re.sub('[()]', '', k)}": float(v) for k, v in model.trainer.metrics.items()}
    # mlflow.log_metrics(metrics=metrics_dict, step=model.trainer.epoch)
    # mlflow.log_artifact(model.trainer.best)
mlflow.log_artifact(__file__)
mlflow.log_artifact('data.yaml')
mlflow.log_artifact('datasets.zip')
mlflow.end_run()
