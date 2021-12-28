# Setup (cloning this repo)
```
cd ~
git clone https://github.com/ecell/bioimage_workflows
```

# Setup (pip install for Ubuntu 20.04)
```
sudo apt update
sudo apt install python3-venv
cd ~
python3 -m venv venv-ecell
source ~/venv-ecell/bin/activate
pip install wheel
pip install mlflow hydra-core scikit-image plotly kaleido azure-storage-blob
pip install git+git://github.com/ecell/scopyon.git@99436fbfd34bb684966846eba75b206c2806f69c
```

# Setup (mlflow server)
```
mlflow server --host 0.0.0.0
```

# Running experiment
```
cd ~/bioimage_workflows
git checkout -t origin/hydra
python -m bioimage_workflow experiment.analysis.params.overlap="range(0.1,1,0.4)" experiment.analysis.params.threshold=40,50 experiment.evaluation.params.max_distance=5.0,6.0,7.0 --multirun
python -m bioimage_workflow experiment.generation.params.Nm="[10,10,10],[100,100,100]" --multirun
```

# Browsing the DWH
Open `http://THE_LOCAL_HOST_IP:5000`
