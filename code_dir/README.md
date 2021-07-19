# Setup

```
sudo apt install python3-pip python3-venv
cd ~
python3 -m venv venv-ecell
source venv-ecell/bin/activate
pip install -U pip
pip install mlflow toml scikit-image plotly kaleido
pip install git+git://github.com/ecell/scopyon.git@99436fbfd34bb684966846eba75b206c2806f69c
```

# Running (mlflow) experiment

```
git clone https://github.com/ecell/bioimage_workflows
cd bioimage_workflows
git checkout -t origin/nocode
cd code_dir
python describe_workflow.py
```
