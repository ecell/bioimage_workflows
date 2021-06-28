from letters_count import *
# mlflow run_starts
# mlflow log_params
ret=count_letters(filename="sample.txt",letter1="a",letter2="e")
# mlflow lgo_artifacts(ret)
# save(./output)
print(ret)
