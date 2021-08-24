import sys
import tempfile

from mlflow import log_metric, log_param, log_artifacts
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.tracking.fluent import _get_experiment_id
from mlflow.utils import mlflow_tags
from mlflow.utils.logging_utils import eprint
from mlflow.entities import RunStatus

# Import our own function
from bioimage_workflow.toml import read_toml

from function_list import kaizu_generation, kaizu_analysis1

tomlpath = "./params.toml"
config = read_toml(tomlpath)
expr_name = config["experiment"]

mlflow.set_tracking_uri(config["tracking_uri"])
tracking_uri = mlflow.get_tracking_uri()
print("Current tracking uri: {}".format(tracking_uri))

if mlflow.get_experiment_by_name(expr_name) is None:
    #mlflow.create_experiment(expr_name, azure_blob)
    mlflow.create_experiment(expr_name)
mlflow.set_experiment(expr_name)

client = MlflowClient()
# from mlflow_utils import _get_or_run

# MLFlow の run を開始する
# ここで、entrypoint名（または、認識できる名前）としてgenerationを渡す。
# mlflowのrunidを習得できるようにしておく。
run_name = 'generation'

with mlflow.start_run(run_name=run_name) as run:
    print(mlflow.get_artifact_uri())
    run = mlflow.active_run()
    gen_params = config["generation"]["params"]
    func = eval(config["generation"]["function"])

    # with tempfile.TemporaryDirectory() as outname:
    #     outpath = pathlib.Path(outname)
    output = func(gen_params)
    for key, value in gen_params.items():
        log_param(key, value)
    print(output)
    log_artifacts(output.replace("file://", ""))
    print(run)

## さきほど取得しておいた、runidをもとに、artifactsを取得するようにする

generation_run_id = run.info.run_id
print("generation_run_id=["+generation_run_id+"]")
generation_artifacts_localpath = client.download_artifacts(run_id=generation_run_id, path="")
print("download from Azure worked!!")
print(generation_artifacts_localpath)
#print("generation_artifacts_localpath=["+generation_artifacts_localpath+"]")
# # generation_artifacts_path = _get_or_run("analysis1", {"generation": generation_run.info.run_id, "threshold": threshold, "min_sigma": min_sigma}, git_commit)

#a["artifacts_pathname"] = generation_artifacts_localpath
run = None
with mlflow.start_run(run_name='analysis1') as run:
    run = mlflow.active_run()
    ana1_params = config["analysis1"]["params"]
    func = eval(config["analysis1"]["function"])
    output = func(ana1_params)
    for key, value in ana1_params.items():
        log_param(key, value)
    print(output)
    log_artifacts(output["artifacts"].replace("file://", ""))
    print(run)

if run is None:
    print("Something wrong at analysis1")

# log_artifacts(output["artifacts"].replace("file://", ""))
# ## toml には書いてあってとしても、generationのrun id
# ## runidから、指定した、フォルダなりファイルを扱うようにする。
# log_metric("num_spots", output["num_spots"])

#
analysis1_run_id = run.info.run_id
print("analysis1_run_id=["+analysis1_run_id+"]")
#analysis1_artifacts_localpath = client.download_artifacts(analysis1_run_id, ".")
#print("analysis1_artifacts_localpath=["+analysis1_artifacts_localpath+"]")
#a["artifacts_pathname"] = analysis1_artifacts_localpath
