#!/bin/bash

for TOMLFILE in `ls config_ana1thre50_*.toml`
do
  python -m bioimage_workflow ${TOMLFILE}
done
