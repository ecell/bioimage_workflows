import subprocess
import mlflow
from mlflow import log_metric, log_param, log_artifacts
import pathlib
import argparse

"""Prepare for generating inputs."""
parser = argparse.ArgumentParser(description='analysis1 step')
parser.add_argument('--threshold', type=float, default=50.0)
parser.add_argument('--num_samples', type=int, default=1)
parser.add_argument('--num_frames', type=int, default=5)
args = parser.parse_args()

num_samples = int(args.num_samples)
num_frames = int(args.num_frames)
threshold = float(args.threshold)

with mlflow.start_run(run_name="main", nested=True):
    # log param
    log_param("threshold", threshold)
    log_param("num_samples", num_samples)
    log_param("num_frames", num_frames)
    # artifacts
    artifacts = pathlib.Path("./artifacts")
    artifacts.mkdir(parents=True, exist_ok=True)
    # generation
    generation_run = mlflow.run(".", "generation", parameters={"num_samples":num_samples, "num_frames":num_frames})
    # analysis1
    analysis1_run = mlflow.run(".", "analysis1", parameters={"threshold":threshold, "num_samples":num_samples})
    # analysis2
    analysis2_run = mlflow.run(".", "analysis2", parameters={"threshold":threshold, "num_samples":num_samples})

#     #log_artifacts("./artifacts")

    evaluation1_run = mlflow.run(".", "evaluation1", parameters={"threshold":threshold, "num_samples":num_samples})
