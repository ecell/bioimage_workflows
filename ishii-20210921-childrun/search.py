import os
import mlflow
from mlflow import log_metric, log_param, log_artifacts

from mlflow.tracking.context.registry import resolve_tags

from mlflow.tracking import MlflowClient
import utils


if __name__ == "__main__":
    client = MlflowClient()
    # runs = client.search_runs(["0"], filter_string="params.step1_x < '2'",order_by=["metrics.step3_z DESC"])
    # for run in runs:
    #     print("---")
    #     print(run)
    print("CHILD_RUN1")
    params= {"step1_x":2,"step2_y":3}
    utils.check_if_already_ran(client, "CHILD_RUN1",params,ignore_tags=False)
    print("CHILD_RUN2")
    utils.check_if_already_ran(client, "CHILD_RUN2",params,ignore_tags=False)

