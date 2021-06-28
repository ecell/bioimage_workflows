from mlflow import log_metric, log_param, log_artifacts

from tomlfunc import read_toml, get_inputs
from workflow import kaizu_generation

a = get_inputs("./test.toml")

for key, value in a.items():
    log_param(key, value)

output = kaizu_generation(a)

print(output)
log_artifacts(output.replace("file://", ""))
