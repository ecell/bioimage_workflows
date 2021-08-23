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
