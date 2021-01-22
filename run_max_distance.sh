#!/bin/bash
max_distances=(50.0 60.0 70.0 80.0 90.0)
for max_distance in ${max_distances[@]}; do
  mlflow run . -e analysis12_evaluation1 -P generation=e3d8393844b9453f9a390e19305d8f3c -P max_distance=${max_distance} --experiment-name  "shareobjectstorage2"
done
