import tempfile
import contextlib
import importlib
import pathlib

import mlflow
from mlflow import log_metric, log_param, log_artifacts


def mkdtemp_persistent(*args, persistent=True, **kwargs):
    if persistent:
        @contextlib.contextmanager
        def normal_mkdtemp():
            yield tempfile.mkdtemp(*args, **kwargs)
        return normal_mkdtemp()
    else:
        return tempfile.TemporaryDirectory(*args, **kwargs)

def get_function(function_path):
    function_path = function_path.split('.')
    module = importlib.import_module('.'.join(function_path[: -1]))
    func = getattr(module, function_path[-1])
    return func

def download_artifacts(client, run_id, path='', dst_path=None):
    print(f'run_id = "{run_id}"')
    dst_path.mkdir()
    artifacts_path = client.download_artifacts(run_id=run_id, path=path, dst_path=str(dst_path))
    # print("download from Azure worked!!")
    print(f'artifacts_path = "{artifacts_path}"')
    return pathlib.Path(artifacts_path)

def run_rule(run_name, config, inputs=(), idx=None, persistent=False, rootpath='.', client=None):
    assert client is not None or len(inputs) == 0

    target = config[run_name] if idx is None else config[run_name][idx]

    with mlflow.start_run(run_name=run_name) as run:
        func_name = target["function"]
        print(f'run_name = "{run_name}", func_name = "{func_name}"')
        print(mlflow.get_artifact_uri())
        run = mlflow.active_run()
        print(f'run_id = "{run.info.run_id}"')
        params = target["params"]
        print(f'params = "{params}"')
        func = get_function(func_name)

        log_param('function', func_name)
        for i, run_id in enumerate(inputs):
            log_param(f'inputs{i}', run_id)
        log_param('output', run.info.run_id)  #XXX: optional

        for key, value in params.items():
            log_param(key, value)

        with mkdtemp_persistent(persistent=persistent, dir=rootpath) as outname:
            working_dir = pathlib.Path(outname)
            input_paths = tuple(download_artifacts(client, run_id, dst_path=working_dir / f'input{i}') for i, run_id in enumerate(inputs))
            output_path = working_dir / 'output'
            output_path.mkdir()
            artifacts, metrics = func(input_paths, output_path, params)
            print(f'artifacts = "{artifacts}"')
            print(f'metrics = "{metrics}"')
            log_artifacts(artifacts.replace("file://", ""))
            for key, value in metrics.items():
                log_metric(key, value)

    if run is None:
        print('Something wrong at "{run_name}"')
    return run



# import sys
# from mlflow import log_metric, log_param, log_artifacts
# import mlflow
# from mlflow.tracking import MlflowClient
# from mlflow.tracking.fluent import _get_experiment_id
# from mlflow.utils import mlflow_tags
# from mlflow.utils.logging_utils import eprint
# from mlflow.entities import RunStatus
# 
# # Import our own function
# from bioimage_workflow.toml import read_toml
# from function_list import kaizu_generation, kaizu_analysis1, kaizu_analysis2
# 
# def _already_ran(run_name, parameters, experiment_id=None):
#     """Best-effort detection of if a run with the given entrypoint name,
#     parameters, and experiment id already ran. The run must have completed
#     successfully and have at least the parameters provided.
#     """
#     experiment_id = experiment_id if experiment_id is not None else _get_experiment_id()
#     client = mlflow.tracking.MlflowClient()
#     all_run_infos = reversed(client.list_run_infos(experiment_id))
#     for run_info in all_run_infos:
#         full_run = client.get_run(run_info.run_id)
#         tags = full_run.data.tags
#         if tags.get(mlflow_tags.MLFLOW_RUN_NAME, None) != run_name:
#             continue
#         match_failed = False
#         for param_key, param_value in parameters.items():
#             run_value = full_run.data.params.get(param_key)
#             if str(run_value) != str(param_value):
#                 match_failed = True
#                 break
#         if match_failed:
#             continue
# 
#         if run_info.to_proto().status != RunStatus.FINISHED:
#             eprint(
#                 ("Run matched, but is not FINISHED, so skipping " "(run_id=%s, status=%s)")
#                 % (run_info.run_id, run_info.status)
#             )
#             continue
# 
#         return client.get_run(run_info.run_id)
#     eprint("No matching run has been found.")
#     return None
# 
# expr_name = "hoge1"
# mlflow.set_tracking_uri("http://11.11.11.11:1111")
# tracking_uri = mlflow.get_tracking_uri()
# print("Current tracking uri: {}".format(tracking_uri))
# 
# if mlflow.get_experiment_by_name(expr_name) is None:
#     #mlflow.create_experiment(expr_name, azure_blob)
#     mlflow.create_experiment(expr_name)
# mlflow.set_experiment(expr_name)
# 
# client = MlflowClient()
# # from mlflow_utils import _get_or_run
# 
# tomlpath = "./params.toml"
# 
# gen_inputs = read_toml(tomlpath)["generation"]["inputs"]
# ana1_inputs = read_toml(tomlpath)["analysis1"]["inputs"]
# ana2_inputs = read_toml(tomlpath)["analysis2"]["inputs"]
# 
# # MLFlow の run を開始する
# # ここで、entrypoint名（または、認識できる名前）としてgenerationを渡す。
# # mlflowのrunidを習得できるようにしておく。
# run_name = 'generation'
# 
# #run = _already_ran(run_name, gen_inputs)
# 
# # if run is None:
# #     # キャッシュがないので、新しく実行する。
# #     with mlflow.start_run(run_name=run_name) as run:
# #         run = mlflow.active_run()
# #         output = kaizu_generation(gen_inputs)
# #         for key, value in gen_inputs.items():
# #             log_param(key, value)
# #         print(output)
# #         # mlflow tracking serverにput
# #         log_artifacts(output.replace("file://", ""))
# #         print(run)
# # else:
# #     print("_already_ran worked!!!")
# 
