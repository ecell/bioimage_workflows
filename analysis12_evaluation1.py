import pathlib
import argparse
import itertools

import mlflow
# from mlflow.utils import mlflow_tags
from mlflow import log_metric, log_param, log_artifacts
from mlflow_utils import _get_or_run

entrypoint = "analysis12_evaluation1"
parser = argparse.ArgumentParser(description='main step')
parser.add_argument('--generation', type=str, default="")
parser.add_argument('--threshold', type=float, default=50.0)
parser.add_argument('--min_sigma', type=int, default=1)
parser.add_argument('--max_distance', type=float, default=50.0)
args = parser.parse_args()

generation = args.generation
threshold = args.threshold
min_sigma = args.min_sigma
max_distance = args.max_distance
client = mlflow.tracking.MlflowClient()
generation_run = client.get_run(generation)

with mlflow.start_run(nested=True) as active_run:
    git_commit = active_run.data.tags.get("mlflow.source.git.commit")
    mlflow.set_tag("mlflow.runName", entrypoint)
    for key, value in vars(args).items():
        log_param(key, value)

    analysis1_run = _get_or_run("analysis1", {"generation": generation, "threshold": threshold, "min_sigma": min_sigma}, git_commit)
    analysis2_run = _get_or_run("analysis2", {"generation": generation, "analysis1": analysis1_run.info.run_id,"max_distance":max_distance}, git_commit)
    evaluation1_run = _get_or_run("evaluation1", {"generation": generation, "analysis1": analysis1_run.info.run_id}, git_commit)

    for run_obj in (generation_run, analysis1_run, analysis2_run, evaluation1_run):
        for key, value in run_obj.data.metrics.items():
            log_metric(key, value)
            
