# Setup (cloning this repo)
```
cd ~
git clone https://github.com/ecell/bioimage_workflows
cd bioimage_workflows
git checkout -t origin/hydra
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
```
cd ~/bioimage_workflows
mlflow server --host 0.0.0.0
```

# Running experiment
```
cd ~/bioimage_workflows
python analysis_evaluation.py
```

# Browsing mlflow tracking server
Open `http://THE_TRACKING_SERVER_IP:5000`
