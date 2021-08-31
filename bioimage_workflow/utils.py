import tempfile
import contextlib
import importlib
import pathlib
import re
import copy

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

def download_artifacts(client, run_id, path='', dst_path=None, exist_ok=False):
    print(f'run_id = "{run_id}"')
    dst_path.mkdir(exist_ok=exist_ok)
    artifacts_path = client.download_artifacts(run_id=run_id, path=path, dst_path=str(dst_path))
    # print("download from Azure worked!!")
    print(f'artifacts_path = "{artifacts_path}"')
    return pathlib.Path(artifacts_path)

def get_rule(target, config):
    if 'function' in target:
        target = copy.deepcopy(target)
        if 'template' in target:
            print(f'The template given is ignored [{run_name}, {idx}].')
            del target['template']
        if 'params' not in target:
            target['params'] = dict()
    elif 'template' in target:
        template = config['template'][target['template']]
        template = copy.deepcopy(template)
        assert 'template' not in template
        if 'params' not in template:
            template['params'] = dict()
        if 'params' in target:
            template['params'].update(target['params'])
        target = template
    elif 'children' in target:
        target = copy.deepcopy(target)
        children = [get_rule(child, config) for child in target['children']]
        target['children'] = children
    else:
        raise RuntimeError(f'The given rule [{target}] has neither function nor template.')

    assert ('function' in target and 'params' in target) or 'children' in target
    assert 'template' not in target
    return target

def run_rule(
        run_name, config, inputs=(), idx=None, persistent=False, rootpath='.', client=None,
        expand=True, use_cache=True, ignore_tags=False):
    target = get_rule(config[run_name] if idx is None else config[run_name][idx], config)
    run_id = __run_rule(
        target, run_name, config, inputs, persistent, rootpath, client, expand, use_cache, ignore_tags)
    return client.get_run(run_id)

def __run_rule(
        target, run_name, config, inputs=(), persistent=False, rootpath='.', client=None,
        expand=True, use_cache=True, ignore_tags=False,
        nested=False, input_paths=None, output_path=None, previous_run_id=None):
    assert client is not None or len(inputs) == 0
    assert not nested or (input_paths is not None and output_path is not None)
    assert nested or (previous_run_id is None)

    if 'function' in target:
        func_name = target["function"]
        print(f'run_name = "{run_name}", func_name = "{func_name}"')
        func = get_function(func_name)

        params = target["params"]
        print(f'params = "{params}"')
        all_params = params.copy()
        assert 'function' not in all_params
        all_params['_function'] = target['function']
    else:
        assert 'children' in target
        params = {}
        all_params = {}
        all_params['_function'] = str([child['function'] for child in target['children']])
        for child in target['children']:
            for key, value in child['params'].items():
                if key in all_params:
                    assert value == all_params[key]
                else:
                    all_params[key] = value
    if previous_run_id is not None:
        all_params['_previous'] = previous_run_id
    for i, run_id in enumerate(inputs):
        key = f'_inputs{i}'
        assert key not in all_params
        all_params[key] = run_id

    if expand:
        for run_id in inputs:
            for key, value in client.get_run(run_id).data.params.items():
                # if key == 'function' or re.match('inputs\d+', key) is not None or key == 'previous':
                if key.startswith('_'):
                    continue
                elif key in all_params:
                    assert value == str(all_params[key])
                    continue
                all_params[key] = value

    print(all_params)
    if use_cache:
        run = check_if_already_ran(client, run_name, all_params, ignore_tags=ignore_tags)
        if run is not None:
            if nested:
                download_artifacts(client, run.info.run_id, dst_path=output_path, exist_ok=True)
            return run.info.run_id

    with mlflow.start_run(run_name=run_name, nested=nested) as run:
        print(mlflow.get_artifact_uri())
        run = mlflow.active_run()
        print(f'run_id = "{run.info.run_id}"')

        for key, value in all_params.items():
            log_param(key, value)

        if not nested:
            with mkdtemp_persistent(persistent=persistent, dir=rootpath) as outname:
                working_dir = pathlib.Path(outname)
                input_paths = tuple(
                    download_artifacts(client, run_id, dst_path=working_dir / f'input{i}')
                    for i, run_id in enumerate(inputs))
                output_path = working_dir / 'output'
                output_path.mkdir()

                if 'children' not in target:
                    artifacts, metrics = func(input_paths, output_path, params)
                    print(f'artifacts = "{artifacts}"')
                    print(f'metrics = "{metrics}"')
                    log_artifacts(artifacts.replace("file://", ""))
                else:
                    previous_run_id = None
                    metrics = {}
                    for child in target['children']:
                        child_run_id = __run_rule(
                            child, run_name, config, inputs, persistent, rootpath,
                            client, expand, use_cache, ignore_tags,
                            nested=True, input_paths=input_paths, output_path=output_path,
                            previous_run_id=previous_run_id)
                        previous_run_id = child_run_id
                        metrics.update(client.get_run(child_run_id).data.metrics)
                        print(f'metrics = "{metrics}"')

                    log_artifacts(output_path.absolute().as_uri().replace("file://", ""))
        else:
            artifacts, metrics = func(input_paths, output_path, params)
            print(f'artifacts = "{artifacts}"')
            print(f'metrics = "{metrics}"')
            log_artifacts(artifacts.replace("file://", ""))

        if expand:
            for run_id in inputs:
                for key, value in client.get_run(run_id).data.metrics.items():
                    if key in metrics:
                        assert value == metrics[key]
                        continue
                    metrics[key] = value

        for key, value in metrics.items():
            log_metric(key, value)

    if run is None:
        print('Something wrong at "{run_name}"')
    return run.info.run_id

from mlflow.utils import mlflow_tags
from mlflow.entities import RunStatus
from mlflow.tracking.fluent import _get_experiment_id
from mlflow.tracking.context.registry import resolve_tags

def check_if_already_ran(client, run_name, params, experiment_id=None, ignore_tags=False):
    """Best-effort detection of if a run with the given entrypoint name,
    parameters, and experiment id already ran. The run must have completed
    successfully and have at least the parameters provided.
    """
    experiment_id = experiment_id if experiment_id is not None else _get_experiment_id()
    all_run_infos = reversed(client.list_run_infos(experiment_id))

    for run_info in all_run_infos:
        full_run = client.get_run(run_info.run_id)

        if run_info.to_proto().status != RunStatus.FINISHED:
            # print("Run matched, but is not FINISHED, so skipping "
            #     + f"(run_id={run_info.run_id}, status={run_info.status})")
            continue

        match_failed = False

        tags = full_run.data.tags
        if not ignore_tags:
            for key, value in resolve_tags().items():
                if value != tags.get(key):
                    match_failed = True
                    break
        else:
            # Only check run_name
            match_failed = match_failed or (tags.get(mlflow_tags.MLFLOW_RUN_NAME, None) != run_name)

        for key, value in params.items():
            if str(value) != str(full_run.data.params.get(key)):
                match_failed = True
                break

        if match_failed:
            continue

        print(f"Matched [{run_info.run_id}]")
        return client.get_run(run_info.run_id)
    print("No matching run has been found.")
    return None
