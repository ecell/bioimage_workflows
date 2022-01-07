import pathlib
import os

import mlflow
from mlflow.tracking import MlflowClient

from .utils import run_rule, __run_rule

import hydra
from omegaconf import DictConfig, OmegaConf
import hydra.utils

@hydra.main(config_path="conf", config_name="config")
def main(cfg: DictConfig):
    expr_name = cfg.experiment.name
    print(f'experiment = {expr_name}')
    print(cfg)
    if os.environ.get("MLFLOW_TRACKING_URI") is None:
        # set_tracking_uri is important for hydra and mlflow integration. if it is local
        mlflow.set_tracking_uri('file://' + hydra.utils.get_original_cwd() + '/mlruns')
    tracking_uri = mlflow.get_tracking_uri()
    print("Current tracking uri: {}".format(tracking_uri))
    if mlflow.get_experiment_by_name(expr_name) is None:
        # mlflow.create_experiment(expr_name, azure_blob)
        mlflow.create_experiment(expr_name)
    mlflow.set_experiment(expr_name)

    client = MlflowClient()

    #client=client is not included in this dictionary in order to enable use_cache.
    run_opts = dict(
        persistent=cfg.experiment.persistent, rootpath=cfg.experiment.rootpath, use_cache=cfg.experiment.use_cache, ignore_tags=cfg.experiment.ignore_tags,
        expand=cfg.experiment.expand,seed=cfg.experiment.generation.params.seed,interval=cfg.experiment.generation.params.interval,num_samples=cfg.experiment.generation.params.num_samples,num_frames=cfg.experiment.generation.params.num_frames,exposure_time=cfg.experiment.generation.params.exposure_time,Nm=cfg.experiment.generation.params.Nm,Dm=cfg.experiment.generation.params.Dm,transmat=cfg.experiment.generation.params.transmat)

    generation = [ __run_rule(target="user_functions.generation1",run_name="generation",config=(),client=client,run_opts=run_opts,persistent=False, rootpath='.',expand=True, use_cache=True, ignore_tags=True)]

    analysis = []
    artifacts_path = generation

    run_opts["min_sigma"] = cfg.experiment.analysis.params.min_sigma
    run_opts["max_sigma"] = cfg.experiment.analysis.params.max_sigma
    run_opts["threshold"] = cfg.experiment.analysis.params.threshold
    run_opts["overlap"] = cfg.experiment.analysis.params.overlap

    analysis = [ __run_rule(target="user_functions.analysis1",run_name="analysis",config=(),client=client,run_opts=run_opts,persistent=False, rootpath='.',expand=True, use_cache=True, ignore_tags=False, inputs=generation)]

    artifacts_path = analysis
    run_opts["max_distance"] = cfg.experiment.evaluation.params.max_distance
    evaluation = [ __run_rule(target="user_functions.evaluation1",run_name="evaluation",config=(),client=client,run_opts=run_opts,persistent=False, rootpath='.',expand=True, use_cache=True, ignore_tags=False, inputs=[generation[0],analysis[0]])]

if __name__ == "__main__":
    main()
    
