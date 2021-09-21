import os
import mlflow
from mlflow import log_metric, log_param, log_artifacts
from mlflow.tracking import MlflowClient
import utils

def step3_sub_z(x,y):
    return x-y

def step2_mul_y(x,y):
    return x*y

def step1_add_x(x):
    return 3+x

def step1_3(client,step1_x,step2_y,step3_z):
    with mlflow.start_run(run_name='PARENT_RUN') as parent_run:
        log_param("parent", "yes")
        log_param("step1_x", step1_x)
        log_param("step2_y", step2_y)
        log_param("step3_z", step3_z)
        result_step1 = 0
        result_step2 = 0
        result_step3 = 0

        with mlflow.start_run(run_name='CHILD_RUN1', nested=True) as child_run:
            past_run=utils.check_if_already_ran(client, "CHILD_RUN1",{"step1_x":step1_x},ignore_tags=False)
            if past_run is None:
                mlflow.set_tags({"original_run":"True","original_run_id":child_run.info.run_id})
                log_param("child1", "yes")
                log_param("step1_x", step1_x)
                result_step1 = step1_add_x(step1_x)
                log_metric("result_step1", float(result_step1))
                # Log an artifact (output file)
                if not os.path.exists("outputs"):
                    os.makedirs("outputs")
                with open("outputs/step1_artifacts.txt", "w") as f:
                    f.write("hello world! step1")
                ## TODO
                log_artifacts("outputs")
            else:
                mlflow.set_tags({"original_run":"False","original_run_id":past_run.info.run_id})
                # log_param("child1", "yes")
                # log_param("step1_x", step1_x)
                # 
                params = past_run.data.params
                for key, value in params.items():
                    log_param(key, value)
                metrics = past_run.data.metrics
                for key, value in metrics.items():
                    log_metric(key, value)
                # TODO copy timestamp ?
                # TODO copy artifact
                result_step1 = float(metrics["result_step1"])
                

        with mlflow.start_run(run_name='CHILD_RUN2', nested=True) as child_run:
            past_run=utils.check_if_already_ran(client, "CHILD_RUN2",{"step1_x":step1_x,"step2_y":step2_y},ignore_tags=False)
            if past_run is None:
                mlflow.set_tags({"original_run":"True","original_run_id":child_run.info.run_id})
                log_param("child2", "yes")
                log_param("step2_y", step2_y)
                result_step2 = step2_mul_y(result_step1,step2_y)
                log_metric("result_step2", float(result_step2))
            else:
                mlflow.set_tags({"original_run":"False","original_run_id":past_run.info.run_id})
                # log_param("child2", "yes")
                # log_param("step2_y", step2_y)
                params = past_run.data.params
                for key, value in params.items():
                    log_param(key, value)
                metrics = past_run.data.metrics
                for key, value in metrics.items():
                    log_metric(key, value)
                # TODO copy timestamp ?
                # TODO copy artifact
                result_step2 = float(metrics["result_step2"])

        with mlflow.start_run(run_name='CHILD_RUN3', nested=True) as child_run:
            past_run=utils.check_if_already_ran(client, "CHILD_RUN3",{"step1_x":step1_x,"step2_y":step2_y,"step3_z":step3_z},ignore_tags=False)
            if past_run is None:
                mlflow.set_tags({"original_run":"True","original_run_id":child_run.info.run_id})
                mlflow.log_param("child3", "yes")
                log_param("step3_z", step3_z)
                result_step3 = step3_sub_z(result_step2,step3_z)
                log_metric("result_step3", float(result_step3))
            else:
                mlflow.set_tags({"original_run":"False","original_run_id":past_run.info.run_id})
                # mlflow.log_param("child3", "yes")
                # log_param("step3_y", step2_y)
                params = past_run.data.params
                for key, value in params.items():
                    log_param(key, value)
                metrics = past_run.data.metrics
                for key, value in metrics.items():
                    log_metric(key, value)
                # TODO copy timestamp ?
                # TODO copy artifact
                result_step3 = float(metrics["result_step3"])
        log_metric("result_step1", result_step1)
        log_metric("result_step2", result_step2)
        log_metric("result_step3", result_step3)
        



if __name__ == "__main__":
    client = MlflowClient()
    # step1_x = 2
    # step2_y = 3
    # step3_z = 4
    # step1_3(client, step1_x, step2_y, step3_z)
    # step1_x = 2
    # step2_y = 3
    # step3_z = 5
    # step1_3(client, step1_x, step2_y, step3_z)
    # step1_x = 1
    # step2_y = 3
    # step3_z = 4
    # step1_3(client, step1_x, step2_y, step3_z)
    # step1_x = 2
    # step2_y = 1
    # step3_z = 5
    # step1_3(client, step1_x, step2_y, step3_z)
    for step1_x in range(1,3):
        for step2_y in range(1,4):
            for step3_z in range(1,5):
                step1_3(client,step1_x, step2_y, step3_z)
