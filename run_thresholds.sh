thresholds=(50.0 60.0 70.0 80.0 90.0)
for t in ${thresholds[@]}; do
  mlflow run . -e analysis12_evaluation1 -P generation=e3d8393844b9453f9a390e19305d8f3c -P threshold=$t --experiment-name  "shareobjectstorage2"
done
