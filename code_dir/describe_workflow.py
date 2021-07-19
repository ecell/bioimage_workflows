from mlflow import log_metric, log_param, log_artifacts
import mlflow
from mlflow.tracking import MlflowClient

# from tomlfunc import read_toml, get_inputs
from tomlfunc import read_toml
from function_list import kaizu_generation, kaizu_analysis1, kaizu_analysis2
#
client = MlflowClient()
# from mlflow_utils import _get_or_run

tomlpath = "./params.toml"

gen_inputs = read_toml(tomlpath)["generation"]["inputs"]
ana1_inputs = read_toml(tomlpath)["analysis1"]["inputs"]
ana2_inputs = read_toml(tomlpath)["analysis2"]["inputs"]

# MLFlow の run を開始する
# ここで、entrypoint名（または、認識できる名前）としてgenerationを渡す。
# mlflowのrunidを習得できるようにしておく。
run = None
with mlflow.start_run(run_name='generation') as run:
    run = mlflow.active_run()
    output = kaizu_generation(gen_inputs)
    for key, value in gen_inputs.items():
        log_param(key, value)
    print(output)
    # mlflow tracking serverにput
    log_artifacts(output.replace("file://", ""))
    print(run)

# if run is None:
#     print("Something wrong at generation")
# for key, value in a.items():
#     log_param(key, value)

## さきほど取得しておいた、runidをもとに、artifactsを取得するようにする
## 適切なディレクトリに対して

generation_run_id = run.info.run_id
print("generation_run_id=["+generation_run_id+"]")
#generation_run_id = "ee5c4443cdbb4048a14a51ea19d9abc0"
generation_artifacts_localpath = client.download_artifacts(generation_run_id, ".")
print("generation_artifacts_localpath=["+generation_artifacts_localpath+"]")
# # generation_artifacts_path = _get_or_run("analysis1", {"generation": generation_run.info.run_id, "threshold": threshold, "min_sigma": min_sigma}, git_commit)

#a["artifacts_pathname"] = generation_artifacts_localpath
run = None
with mlflow.start_run(run_name='analysis1') as run:
    run = mlflow.active_run()
    output = kaizu_analysis1(ana1_inputs)
    for key, value in ana1_inputs.items():
        log_param(key, value)
    print(output)
    # mlflow tracking serverにput
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
analysis1_artifacts_localpath = client.download_artifacts(analysis1_run_id, ".")
print("analysis1_artifacts_localpath=["+analysis1_artifacts_localpath+"]")
#a["artifacts_pathname"] = analysis1_artifacts_localpath
run = None
with mlflow.start_run(run_name='analysis2') as run:
    run = mlflow.active_run()
    output = kaizu_analysis2(ana2_inputs, generation_artifacts_localpath, analysis1_artifacts_localpath)
    for key, value in ana2_inputs.items():
        log_param(key, value)
    print(output)
    # mlflow tracking serverにput
    log_artifacts(output["artifacts"].replace("file://", ""))
    print(run)

if run is None:
    print("Something wrong at analysis2")
