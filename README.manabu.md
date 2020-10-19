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

## 各ステップの説明

### Step1

- `seed` でパラメータを受け取り
- `seedplus1` で、 `seed` に1加えたものを返す

```python
    mlflow.log_param("seed", seed)
    mlflow.log_metric("seedplus1", seed+1)
```

### Step2

- `inputval1` でパラメータを受け取り
- `doubledinput` に　`inputval1` に１を加えたものを返す

```python
    mlflow.log_param("inputval1", inputval1)
    mlflow.log_metric("doubledinput", inputval1*2)
```

### Step3

- `step3inputval1` でパラメータを受け取り
- `sub3` に、`step3inputval1`から３引いたものを返す

```python
    mlflow.log_param("step3inputval1", step3inputval1)
    mlflow.log_metric("sub3", step3inputval1-3)
```

### Step2 and Step3

`inputval` で渡されたものを２倍して３を引いたものを返す

- `inputval1` でパラメータを受け取る
    - `doubledinput` に　`inputval1` に１を加えたものを返す
- `step3inputval1` は、`doubledinput`を受け取る
    - `sub3` に、`step3inputval1`から３引いたものを返す


#### 例

```
mlflow run -e exec_step2_and_step3 . -P inputval1=3000
```

実行が終わった直後

![実行直後](./Screen%20Shot%202020-10-19%20at%2013.56.04.png)

ネストしているものを展開したところ

![ネストを展開したあと](Screen%20Shot%202020-10-19%20at%2013.56.13.png)

