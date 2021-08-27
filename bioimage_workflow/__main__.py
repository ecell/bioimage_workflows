import pathlib

import mlflow
from mlflow.tracking import MlflowClient

from .toml import read_toml
from .utils import run_rule


def main(filename, tracking_uri, rootpath, persistent, use_cache, ignore_tags):
    config = read_toml(filename)
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

    run_opts = dict(
        persistent=persistent, rootpath=rootpath, client=client, use_cache=use_cache, ignore_tags=ignore_tags)

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

if __name__ == "__main__":
    import os
    tracking_uri = os.environ["MLFLOW_TRACKING_URI"]

    import argparse
    parser = argparse.ArgumentParser(description='Run the workflow')
    parser.add_argument('inputs', type=str, nargs='*', help='Input toml files ("./config.toml")')
    parser.add_argument(
        '-p', '--persistent', action='store_true', help='Stop removing temporal aritfact directories')
    parser.add_argument(
        '--no-cache', action='store_true', help='Never skip even when the same run has been already run')
    parser.add_argument(
        '--ignore-tags', action='store_true', help='Ignore tags except for run_name when comparing runs')
    parser.add_argument(
        '-o', '--output', default='artifacts',
        help='Set the root directory for reserving artifacts locally ("./artifacts")')
    args = parser.parse_args()

    persistent = args.persistent
    use_cache = not args.no_cache
    ignore_tags = args.ignore_tags

    rootpath = pathlib.Path(args.output)
    rootpath.mkdir(parents=True, exist_ok=True)

    if len(args.inputs) == 0:
        main('config.toml', tracking_uri, rootpath, persistent, use_cache, ignore_tags)
    else:
        for filename in args.inputs:
            main(filename, tracking_uri, rootpath, persistent, use_cache, ignore_tags)
