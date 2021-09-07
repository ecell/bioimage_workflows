#!/bin/bash

for TOMLFILE in `ls *.toml`
do
  python -m bioimage_workflow ${TOMLFILE}
done
