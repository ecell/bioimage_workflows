import sys
import tempfile
import pathlib
import importlib

from mlflow import log_metric, log_param, log_artifacts
import mlflow
from mlflow.tracking import MlflowClient
from mlflow.tracking.fluent import _get_experiment_id
from mlflow.utils import mlflow_tags
from mlflow.utils.logging_utils import eprint
from mlflow.entities import RunStatus

# Import our own function
from bioimage_workflow.toml import read_toml
from bioimage_workflow.utils import mkdtemp_persistent


def get_function(function_path):
    function_path = function_path.split('.')
    module = importlib.import_module('.'.join(function_path[: -1]))
    func = getattr(module, function_path[-1])
    return func

def download_artifacts(run_id, path='', dst_path=None):
    print(f'run_id = "{run_id}"')
    dst_path.mkdir()
    artifacts_path = client.download_artifacts(run_id=run_id, path=path, dst_path=str(dst_path))
    print("download from Azure worked!!")
    print(f'artifacts_path = "{artifacts_path}"')
    return pathlib.Path(artifacts_path)

def run_rule(run_name, config, inputs=(), idx=None, persistent=False, rootpath='.'):
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

        for i, run_id in enumerate(inputs):
            log_param(f'inputs{i}', run_id)
        log_param('output', run.info.run_id)  #XXX: optional

        for key, value in params.items():
            log_param(key, value)

        with mkdtemp_persistent(persistent=persistent, dir=rootpath) as outname:
            working_dir = pathlib.Path(outname)
            input_paths = tuple(download_artifacts(run_id, dst_path=working_dir / f'input{i}') for i, run_id in enumerate(inputs))
            output_path = working_dir / 'output'
            output_path.mkdir()
            artifacts, metrics = func(input_paths, output_path, params)
            print(f'artifacts = "{artifacts}"')
            print(f'metrics = "{metrics}"')
            log_artifacts(artifacts.replace("file://", ""))
            for key, value in metrics.items():
                log_metric(key, value)
    return run


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Run the workflow')
    parser.add_argument('-p', '--persistent', help='Stop removing temporal aritfact directories', action='store_true')
    parser.add_argument('-i', '--input', help='A toml file ("./config.toml")', default='config.toml')
    parser.add_argument('-o', '--output', help='Set the root directory for reserving artifacts locally ("./artifacts")', default='artifacts')
    args = parser.parse_args()

    persistent = args.persistent

    rootpath = pathlib.Path(args.output)
    rootpath.mkdir(parents=True, exist_ok=True)

    config = read_toml(args.input)
    expr_name = config["experiment"]

    mlflow.set_tracking_uri(config["tracking_uri"])
    tracking_uri = mlflow.get_tracking_uri()
    print("Current tracking uri: {}".format(tracking_uri))

    if mlflow.get_experiment_by_name(expr_name) is None:
        #mlflow.create_experiment(expr_name, azure_blob)
        mlflow.create_experiment(expr_name)
    mlflow.set_experiment(expr_name)

    client = MlflowClient()

    # MLFlow の run を開始する
    # ここで、entrypoint名（または、認識できる名前）としてgenerationを渡す。
    # mlflowのrunidを習得できるようにしておく。

    # run = run_rule('generation', config, inputs=(), idx=0, persistent=persistent, rootpath=rootpath)
    generation = [run_rule('generation', config, inputs=(), idx=idx, persistent=persistent, rootpath=rootpath) for idx in range(len(config['generation']))]

    ## さきほど取得しておいた、runidをもとに、artifactsを取得するようにする

    for generation_run in generation:
        generation_run_id = generation_run.info.run_id

        for idx in range(len(config['analysis'])):
            run = run_rule('analysis', config, inputs=(generation_run_id, ), idx=idx, persistent=persistent, rootpath=rootpath)

            if run is None:
                print("Something wrong at analysis")

    # ## toml には書いてあってとしても、generationのrun id
    # ## runidから、指定した、フォルダなりファイルを扱うようにする。
