# Setup (cloning this repo)
```
cd ~
git clone https://github.com/ecell/bioimage_workflows
cd bioimage_workflows
git checkout -t origin/optuna_ishii
```

# Setup (pip install for Ubuntu 20.04)
```
sudo apt update
sudo apt install python3-venv
cd ~
python3 -m venv venv-ecell
source ~/venv-ecell/bin/activate
pip install wheel
pip install mlflow==1.30.0 hmmlearn==0.2.6 hydra-core scikit-image plotly kaleido azure-storage-blob
pip install git+https://github.com/ecell/scopyon.git@99436fbfd34bb684966846eba75b206c2806f69c
pip install optuna==3.0.5 protobuf==3.20.3 optuna-dashboard==0.8.1
```

# Running mlflow tracking server

## Tracking server directory

```
cd ~/bioimage_workflows
mlflow server --host 0.0.0.0
```

## Tracking server with docker

Run with uid and gid of the starting user.
All data is located at `$HOME/mlflowbackend`

```
mkdir $HOME/mlflowbackend
docker run --rm --user `id -u`:`id -g` -p 5000:5000  -v $HOME/mlflowbackend:/backend ghcr.io/mlflow/mlflow:v1.30.0 mlflow server --host 0.0.0.0 --backend-store-uri sqlite:////backend/tracking.db --artifacts-destination file:///backend/artifacts --serve-artifacts
```

# Running experiment
```
cd ~/bioimage_workflows
python analysis_evaluation.py
```

# Browsing mlflow tracking server
Open `http://THE_TRACKING_SERVER_IP:5000`
