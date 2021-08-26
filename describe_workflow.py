import pathlib

import mlflow
from mlflow.tracking import MlflowClient

from bioimage_workflow.toml import read_toml
from bioimage_workflow.utils import run_rule


if __name__ == "__main__":
    import argparse
    import os

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

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
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
    generation = [run_rule('generation', config, inputs=(), idx=idx, persistent=persistent, rootpath=rootpath, client=client) for idx in range(len(config['generation']))]

    ## さきほど取得しておいた、runidをもとに、artifactsを取得するようにする

    for generation_run in generation:
        generation_run_id = generation_run.info.run_id

        for analysis_idx in range(len(config['analysis'])):
            analysis_run = run_rule('analysis', config, inputs=(generation_run_id, ), idx=analysis_idx, persistent=persistent, rootpath=rootpath, client=client)
            for evaluation_idx in range(len(config['evaluation'])):
                evaluation_run = run_rule('evaluation', config, inputs=(generation_run_id, analysis_run.info.run_id), idx=evaluation_idx, persistent=persistent, rootpath=rootpath, client=client)

    # ## toml には書いてあってとしても、generationのrun id
    # ## runidから、指定した、フォルダなりファイルを扱うようにする。
