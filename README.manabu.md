# Prerequisite

```
conda activate mlflow
```

## Exec MLProject main project

```
cd ..
mlflow run bioimage_workflows -P seed=100 
```

## Exec MLProject exec_step2_and_step3 project

```
cd ..
mlflow run -e exec_step2_and_step3 bioimage_workflows -P inputval1=100 
```
