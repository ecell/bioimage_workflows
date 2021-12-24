import pathlib

import mlflow
from mlflow.tracking import MlflowClient

from .utils import run_rule, __run_rule

import hydra
from omegaconf import DictConfig, OmegaConf


@hydra.main(config_path="conf", config_name="config")
def main(cfg: DictConfig):
# def main(filename, tracking_uri, rootpath, persistent, use_cache, ignore_tags, expand):
    #print(f'filename = {filename}')
    #config = read_toml(filename)
    #expr_name = config["experiment"]
    expr_name = cfg.experiment.name
    print(f'experiment = {expr_name}')
    print(cfg)

    # just checking ...
    # print("rootpath is ...")
    # print(rootpath)
    # print("persistent is ...")
    # print(persistent)
    # print("use_cache is ...")
    # print(use_cache)
    # print("ignore_tags is ...")
    # print(ignore_tags)
    # print("expand is ...")
    # print(expand)

    #mlflow.set_tracking_uri(tracking_uri)
    #mlflow.set_tracking_uri("/home/azureuser/bioimage_workflows/outputs/2021-11-05/05-12-27/mlruns/1")
    #mlflow.set_tracking_uri("./hoge/mlruns/")
    tracking_uri = mlflow.get_tracking_uri()

    print("Current tracking uri: {}".format(tracking_uri))
    #sys.exit(0)
    if mlflow.get_experiment_by_name(expr_name) is None:
        # mlflow.create_experiment(expr_name, azure_blob)
        mlflow.create_experiment(expr_name)
    mlflow.set_experiment(expr_name)

    client = MlflowClient()

    # run_opts = dict(
    #     persistent=persistent, rootpath=rootpath, client=client, use_cache=use_cache, ignore_tags=ignore_tags,
    #     expand=expand)

    run_opts = dict(
        persistent=cfg.experiment.persistent, rootpath=cfg.experiment.rootpath, client=client, use_cache=cfg.experiment.use_cache, ignore_tags=cfg.experiment.ignore_tags,
        expand=cfg.experiment.expand,seed=cfg.experiment.generation.params.seed,interval=cfg.experiment.generation.params.interval,num_samples=cfg.experiment.generation.params.num_samples,num_frames=cfg.experiment.generation.params.num_frames,exposure_time=cfg.experiment.generation.params.exposure_time,Nm=cfg.experiment.generation.params.Nm,Dm=cfg.experiment.generation.params.Dm,transmat=cfg.experiment.generation.params.transmat)

    #XXX: generation
    # generation = [
    #     (run_rule('generation', config, inputs=(), idx=idx, **run_opts).info.run_id, )
    #     for idx in range(len(config['generation']))]
# def __run_rule(
#         target, run_name, config, inputs=(), persistent=False, rootpath='.', client=None,
#         expand=True, use_cache=True, ignore_tags=False,
#         nested=False, input_paths=None, output_path=None, previous_run_id=None):
    # MEMO: inputs is ()
    generation = [ __run_rule(target="user_functions.generation1",run_name="generation",config=(),client=client,run_opts=run_opts,persistent=False, rootpath='.',expand=True, use_cache=True, ignore_tags=False)]


#    if 'analysis' not in config:
#        return

    #XXX: analysis
    analysis = []
    #artifacts_path =["f4c1e9666d414ebfa64ad483ad7c7e3b"]
    artifacts_path = generation

    run_opts["min_sigma"] = cfg.experiment.analysis.params.min_sigma
    run_opts["max_sigma"] = cfg.experiment.analysis.params.max_sigma
    run_opts["threshold"] = cfg.experiment.analysis.params.threshold
    run_opts["overlap"] = cfg.experiment.analysis.params.overlap

    analysis = [ __run_rule(target="user_functions.analysis1",run_name="analysis",config=(),client=client,run_opts=run_opts,persistent=False, rootpath='.',expand=True, use_cache=True, ignore_tags=False, inputs=generation)]

#    for idx in range(len(config['analysis'])):
#        for inputs in generation:
#            run = run_rule('analysis', config, inputs=inputs, idx=idx, **run_opts)
#            analysis.append(inputs + (run.info.run_id, ))

    # for evaluation
    # set analysis in artifacts_path 
    artifacts_path = analysis
    run_opts["max_distance"] = cfg.experiment.evaluation.params.max_distance
    evaluation = [ __run_rule(target="user_functions.evaluation1",run_name="evaluation",config=(),client=client,run_opts=run_opts,persistent=False, rootpath='.',expand=True, use_cache=True, ignore_tags=False, inputs=[generation[0],analysis[0]])]
    #if 'evaluation' not in config:
    #    return

    #XXX: evaluation
#   for idx in range(len(config['evaluation'])):
#        for inputs in analysis:
#            run = run_rule('evaluation', config, inputs=inputs, idx=idx, **run_opts)

if __name__ == "__main__":
    main()
    # import os
    # tracking_uri = os.environ["MLFLOW_TRACKING_URI"]
    # tracking_uri = "hoge"

    # import argparse
    # parser = argparse.ArgumentParser(description='Run the workflow')
    # parser.add_argument('inputs', type=str, nargs='*', help='Input toml files ("./config.toml")')
    # parser.add_argument(
    #     '-p', '--persistent', action='store_true', help='Stop removing temporal aritfact directories')
    # parser.add_argument(
    #     '-x', '--expand', action='store_true', help='Expand parameters')
    # parser.add_argument(
    #     '--no-cache', action='store_true', help='Never skip even when the same run has been already run')
    # parser.add_argument(
    #     '--ignore-tags', action='store_true', help='Ignore tags except for run_name when comparing runs')
    # parser.add_argument(
    #     '-o', '--output', default='artifacts',
    #     help='Set the root directory for reserving artifacts locally ("./artifacts")')
    # args = parser.parse_args()

    # persistent = args.persistent
    # use_cache = not args.no_cache
    # ignore_tags = args.ignore_tags
    # expand = args.expand

    # rootpath = pathlib.Path(args.output)
    # rootpath.mkdir(parents=True, exist_ok=True)

    # if len(args.inputs) == 0:
    #     # main('config.toml', tracking_uri, rootpath, persistent, use_cache, ignore_tags, expand)
    #     #main(hoge="hoge")
    #     main()
    # else:
    #     for filename in args.inputs:
    #         main(filename, tracking_uri, rootpath, persistent, use_cache, ignore_tags, expand)
