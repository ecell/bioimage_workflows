# bioimage_workflows

## System Requirements

- Ubuntu Linux 18.04 (This workflow does not work in WSL2 environment due to the uniqueness of the file system)

## Setup mlflow environment

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
1. run `pip install mlflow` with Miniconda's pip

## Setup environment variables

If you use S3 or S3 compatible siystem like [MINIO](https://min.io/),
 you need to set up these environment variables

```
export AWS_DEFAULT_REGION=ap-northeast-1
export AWS_ACCESS_KEY_ID=YOURMINIOACCESSKEY
export AWS_SECRET_ACCESS_KEY=YOURMINIOSECRETKEY
export MLFLOW_S3_ENDPOINT_URL=http://xxx.xxx.xxx.xxx:yyyy/
```

## Setup mlflow server

1. run `tmux` to create multiple shells and save the processes
1. run `mlflow ui -h 0.0.0.0` and create a new tmux pane

## How to run this workflow

1. run `tmux` to create multiple shells and save the processes
1. move to the another tmux pane and run `mlflow run https://github.com/ecell/bioimage_workflows.git`

## How to run specific workflow which is written as entrypoint

If you want to execute `analysis1` in entrypoint, command is following

`mlflow run -e analysis1 https://github.com/ecell/bioimage_workflows.git -P num_samples=1 -P num_frames=5`

## How to run with specific experiment name

If you want to execute `myexperiment1` in experiment, command is following

`mlflow run -e analysis1 https://github.com/ecell/bioimage_workflows.git -P num_samples=1 -P num_frames=5 --experiment-name "myexperiment1"`

## How to run with specific git commit id

If you want to execute git commit id `"40b29386"`, command is following

`mlflow run -e analysis1 https://github.com/ecell/bioimage_workflows.git -P num_samples=1 -P num_frames=5 --experiment-name "myexperiment1" --version "40b29386"`
