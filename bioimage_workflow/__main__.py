import pathlib

import mlflow
from mlflow.tracking import MlflowClient

from .toml import read_toml
from .utils import run_rule


if __name__ == "__main__":
    import os
    tracking_uri = os.environ["MLFLOW_TRACKING_URI"]

    import argparse
    parser = argparse.ArgumentParser(description='Run the workflow')
    parser.add_argument(
        '-p', '--persistent', action='store_true', help='Stop removing temporal aritfact directories')
    parser.add_argument(
        '-i', '--input', default='config.toml', help='A toml file ("./config.toml")')
    parser.add_argument(
        '-o', '--output', default='artifacts',
        help='Set the root directory for reserving artifacts locally ("./artifacts")')
    args = parser.parse_args()

    persistent = args.persistent

    rootpath = pathlib.Path(args.output)
    rootpath.mkdir(parents=True, exist_ok=True)

    config = read_toml(args.input)
    expr_name = config["experiment"]
    print(f'experiment = {expr_name}')

    mlflow.set_tracking_uri(tracking_uri)
    tracking_uri = mlflow.get_tracking_uri()
    print("Current tracking uri: {}".format(tracking_uri))

    if mlflow.get_experiment_by_name(expr_name) is None:
        # mlflow.create_experiment(expr_name, azure_blob)
        mlflow.create_experiment(expr_name)
    mlflow.set_experiment(expr_name)

    client = MlflowClient()

    run_opts = dict(persistent=persistent, rootpath=rootpath, client=client)

    #XXX: generation
    generation = [
        (run_rule('generation', config, inputs=(), idx=idx, **run_opts).info.run_id, )
        for idx in range(len(config['generation']))]

    #XXX: analysis
    analysis = []
    for idx in range(len(config['analysis'])):
        for inputs in generation:
            run = run_rule('analysis', config, inputs=inputs, idx=idx, **run_opts)
            analysis.append(inputs + (run.info.run_id, ))

    #XXX: evaluation
    for idx in range(len(config['evaluation'])):
        for inputs in analysis:
            run = run_rule('evaluation', config, inputs=inputs, idx=idx, **run_opts)
