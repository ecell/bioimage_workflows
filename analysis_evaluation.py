#!/usr/bin/python
# Setup MLflow server
#  cd work/bioimage_workflows/
#  source ~/venv-ecell/bin/activate
#  mlflow server --host 0.0.0.0
# Start Optuna
#  cd work/bioimage_workflows/
#  source ~/venv-ecell/bin/activate
# Run Sample
#  python generation_analysis.py
# 
import optuna
import mlflow
from optuna.integration.mlflow import MLflowCallback
from user_functions import generation1, analysis1, evaluation1
from pathlib import Path
from mlflow import MlflowClient
from bioimage_workflow.utils import check_if_already_ran
import sys

mlflc = MLflowCallback(
    tracking_uri="http://127.0.0.1:5000",
    metric_name="sum of square x_mean and y_mean",
)

# generation data pass as global variable
# Add generation to mlflow


generation_params = {
    "seed": 123,
    "interval": 0.033,
    "num_samples": 1,
    "num_frames": 2,
    "exposure_time": 0.033,
    "Nm": [100, 100, 100],
    "Dm": [0.222e-12, 0.032e-12, 0.008e-12],
    "transmat": [
        [0.0, 0.5, 0.0],
        [0.5, 0.0, 0.2],
        [0.0, 1.0, 0.0]]
}

analysis_params = {
    "max_sigma": 4,
    "min_sigma": 1,
    "threshold": 50.0,
    "overlap": 0.5
}

evaluation_params = {
    "max_distance": 5.0
}

exposure_time=0

@mlflc.track_in_mlflow()
def objective(trial):
    # variables for analysis.
    global generation_params, analysis_params, evaluation_params, exposure_time

    generation_params["exposure_time"] = exposure_time

    client = MlflowClient(tracking_uri="http://127.0.0.1:5000")
    # print("--- cleint")
    # print(dir(client))
    # from mlflow.tracking.fluent import _get_experiment_id
    # experiment_id = _get_experiment_id()
    # print(experiment_id)
    # all_run_infos = reversed(client.list_run_infos(experiment_id))
    # print(all_run_infos)
    # for ru in all_run_infos:
    #     print(ru)


    ## NOTE: ignore_tags is False, so name is not checked, it checks only params
    local_artifacts_dir="./artifacts/"
    run=check_if_already_ran(client,"", generation_params)
    if run is None:
        # Exec generation
        with mlflow.start_run(nested=True, run_name="generation_"+str(trial.number)) as run_analysis:
            generation_output=Path(local_artifacts_dir+'/'+run_analysis.info.run_id)
            print(str(generation_output))
            if not generation_output.exists():
                generation_output.mkdir(parents=True, exist_ok=True)

            artifacts,metrics = generation1([], generation_output, generation_params)
            for key, value in generation_params.items():
                mlflow.log_param(key, value)
            #
            mlflow.log_artifacts(str(generation_output))
    else:
        #
        generation_output=Path(local_artifacts_dir+'/'+run.info.run_id)
        if not generation_output.exists():
            generation_output.mkdir(parents=True, exist_ok=True)
            client.download_artifacts(run_id=run.info.run_id, path="", dst_path=str(generation_output))

    # sys.exit()

    # print()
    # print(dir(trial))
    # exit()
    # call analysis
    # input
    # generation_output=Path('./outputs_generation')
    # analysis output
    # create new dir, use trial.number
    analysis_output=Path('./outputs_analysis_run/'+str(trial.number))
    analysis_output.mkdir(parents=True, exist_ok=True)
    overlap = trial.suggest_float("overlap", 0, 1)
    threshold = trial.suggest_float("threshold", 30, 70)

    with mlflow.start_run(nested=True, run_name="analysis_"+str(trial.number)) as run_analysis:
        # set param
        analysis_params["overlap"]=overlap
        analysis_params["threshold"]=threshold
        
        a,b = analysis1([generation_output], analysis_output, analysis_params)
        num_spots = b["num_spots"]
        # Set param
        mlflow.log_param("overlap", overlap)
        mlflow.log_param("threshold", threshold)

        # Set metric
        mlflow.log_metric("num_spots", num_spots)
        # End analysis run
        # mlflow.end_run()
    
    ## call evaluation
    # output
    evaluation_output=Path('./outputs_evaluation_run/'+str(trial.number))
    evaluation_output.mkdir(parents=True, exist_ok=True)

    # max_distance = trial.suggest_float("max_distance", 0, 1)
    max_distance = evaluation_params["max_distance"]

    mlflow.log_param("overlap", overlap)
    mlflow.log_param("threshold", threshold)

    mlflow.log_param("max_distance", max_distance)
    
    evaluation_params["max_distance"] = max_distance
    c,d = evaluation1([generation_output,analysis_output], evaluation_output, evaluation_params)

    x_mean = d["x_mean"]
    y_mean = d["y_mean"]

    mlflow.log_metric("x_mean", x_mean)
    mlflow.log_metric("y_mean", y_mean)

    # TODO: not hard code 600
    result = (x_mean)**2+(y_mean)**2
    return result



def main():
    global generation_params,analysis_params, exposure_time
    # Setup for Optuna MLFlow
    # generation_output=Path('./outputs_generation')
    # generation1([], generation_output, generation_params)

    # analysis_output=Path('./outputs_analysis')
    
    # a,b = analysis1([generation_output], analysis_output, analysis_params)
    # print(a)
    # print(b)
    # Execute Optuna MLFlow
    study = optuna.create_study(storage="sqlite:///example2.db", study_name="test_x_y_mean_storage_6", load_if_exists=True, sampler=optuna.samplers.CmaEsSampler())
    # print("--- study")
    # print(dir(study))
    for i in range(5):
        exposure_time=exposure_time+0.033
        study.optimize(objective, n_trials=5, callbacks=[mlflc])
        print(study.best_params)

    # ここで別のexperimentにoptuna記録するという方法もある。

# print("--- mlflc")
# print(dir(mlflc))

if __name__ == "__main__":
    main()
