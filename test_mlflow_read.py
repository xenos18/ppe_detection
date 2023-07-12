import mlflow
from mlflow import MlflowClient
import os
from dotenv import load_dotenv
load_dotenv()


MLFLOW_PORT = os.environ['MLFLOW_PORT']

mlflow.set_tracking_uri(f"http://localhost:{MLFLOW_PORT}")

client = MlflowClient()
experiment = client.get_experiment_by_name("siz-object-detection")
print(type(experiment))