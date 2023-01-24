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
from user_functions import generation1, analysis1
from pathlib import Path

mlflc = MLflowCallback(
    tracking_uri="http://127.0.0.1:5000",
    metric_name="test num_spot",
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


@mlflc.track_in_mlflow()
def objective(trial):
    # variables for analysis.
    global analysis_params

    # call analysis
    # input
    generation_output=Path('./outputs_generation')
    # output
    analysis_output=Path('./outputs_analysis')
    # set param
    overlap = trial.suggest_float("overlap", 0, 1)
    threshold = trial.suggest_float("threshold", 30, 70)
    analysis_params["overlap"]=overlap
    analysis_params["threshold"]=threshold
    
    a,b = analysis1([generation_output], analysis_output, analysis_params)
    num_spots = b["num_spots"]
    
    # Set param
    mlflow.log_param("overlap", overlap)
    mlflow.log_param("threshold", threshold)

    # Set metric
    mlflow.log_metric("num_spots", num_spots)

    # TODO: not hard code 600
    result = (num_spots - 600)**2
    return result



def main():
    global generation_params,analysis_params
    # Setup for Optuna MLFlow
    # generation_output=Path('./outputs_generation')
    # generation1([], generation_output, generation_params)

    # analysis_output=Path('./outputs_analysis')
    
    # a,b = analysis1([generation_output], analysis_output, analysis_params)
    # print(a)
    # print(b)
    # Execute Optuna MLFlow
    study = optuna.create_study(study_name="test_num_spot_6")
    study.optimize(objective, n_trials=20, callbacks=[mlflc])
    print(study.best_params)

if __name__ == "__main__":
    main()
