#!/bin/bash

for TOMLFILE in `ls *.toml`
do
  echo "python -m bioimage_workflow ${TOMLFILE}"
done
