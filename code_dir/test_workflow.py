from mlflow import log_metric, log_param, log_artifacts

from tomlfunc import read_toml, get_inputs
from workflow import kaizu_generation, kaizu_analysis1

a = get_inputs("./test.toml")

for key, value in a.items():
    log_param(key, value)
#output = kaizu_generation(a)
#print(output)
#log_artifacts(output.replace("file://", ""))

for key, value in a.items():
    log_param(key, value)

output = kaizu_analysis1(a)
log_artifacts(output["artifacts"].replace("file://", ""))
log_metric("num_spots", output["num_spots"])
