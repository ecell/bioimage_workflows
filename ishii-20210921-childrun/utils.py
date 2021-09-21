from mlflow.entities import RunStatus

from mlflow.utils import mlflow_tags

from mlflow.tracking import MlflowClient
from mlflow.tracking.fluent import _get_experiment_id

def check_if_already_ran_each(client, run_name, params, experiment_id=None, ignore_tags=False,search_tags=None):
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
        #print(run_info.run_id)
        match_failed = False

        tags = full_run.data.tags
        if not ignore_tags:
            # print(tags)
            if search_tags is not None:
                for key, value in search_tags.items():
                    if value != tags.get(key):
                        match_failed = True
                        break
        else:
            # Only check run_name
            # print(tags)
            #print(tags.get(mlflow_tags.MLFLOW_RUN_NAME))
            match_failed = match_failed or (tags.get(mlflow_tags.MLFLOW_RUN_NAME, None) != run_name)

        for key, value in params.items():
            if str(value) != str(full_run.data.params.get(key)):
                match_failed = True
                break

        if match_failed:
            continue

        # print(f"Matched [{run_info.run_id}]")
        return client.get_run(run_info.run_id)
    # print("No matching run has been found.")
    return None


def check_if_already_ran(client, run_name, params, experiment_id=None, ignore_tags=False,search_tags=None):
    """Best-effort detection of if a run with the given entrypoint name,
    parameters, and experiment id already ran. The run must have completed
    successfully and have at least the parameters provided.
    """
    experiment_id = experiment_id if experiment_id is not None else _get_experiment_id()
    parent_run = check_if_already_ran_each(client,"PARENT_RUN",params,experiment_id=experiment_id,ignore_tags=False,search_tags=search_tags)
    if parent_run is None:
        return None
    if run_name == "CHILD_RUN1":
        child_run1_params = {"step1_x": params["step1_x"]}
        child_run1_tags = { "mlflow.parentRunId": parent_run.info.run_id}
        child_run = check_if_already_ran_each(client,"CHILD_RUN1",child_run1_params, experiment_id=experiment_id,ignore_tags=False,search_tags=child_run1_tags)
        if child_run is None:
            # Something wrong
            print("Something wrong RUN1")
            return None
        return child_run
    if run_name == "CHILD_RUN2":
        child_run2_params = {"step2_y": params["step2_y"]}
        child_run2_tags = { "mlflow.parentRunId": parent_run.info.run_id}
        child_run = check_if_already_ran_each(client,"CHILD_RUN2",child_run2_params, experiment_id=experiment_id,ignore_tags=False,search_tags=child_run2_tags)
        if child_run is None:
            # Something wrong
            print("Something wrong")
            return None
        return child_run
    if run_name == "CHILD_RUN3":
        child_run3_params = {"step3_z": params["step3_z"]}
        child_run3_tags = { "mlflow.parentRunId": parent_run.info.run_id}
        child_run = check_if_already_ran_each(client,"CHILD_RUN3",child_run3_params, experiment_id=experiment_id,ignore_tags=False,search_tags=child_run3_tags)
        if child_run is None:
            # Something wrong
            print("Something wrong")
            return None
        return child_run


    all_run_infos = reversed(client.list_run_infos(experiment_id))

    for run_info in all_run_infos:
        full_run = client.get_run(run_info.run_id)

        if run_info.to_proto().status != RunStatus.FINISHED:
            # print("Run matched, but is not FINISHED, so skipping "
            #     + f"(run_id={run_info.run_id}, status={run_info.status})")
            continue
        #print(run_info.run_id)
        match_failed = False

        tags = full_run.data.tags
        if not ignore_tags:
            # print(tags)
            if search_tags is not None:
                for key, value in search_tags.items():
                    if value != tags.get(key):
                        match_failed = True
                        break
        else:
            # Only check run_name
            # print(tags)
            #print(tags.get(mlflow_tags.MLFLOW_RUN_NAME))
            match_failed = match_failed or (tags.get(mlflow_tags.MLFLOW_RUN_NAME, None) != run_name)

        for key, value in params.items():
            if str(value) != str(full_run.data.params.get(key)):
                match_failed = True
                break

        if match_failed:
            continue

        # print(f"Matched [{run_info.run_id}]")
        return client.get_run(run_info.run_id)
    # print("No matching run has been found.")
    return None
    
