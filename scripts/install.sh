#!/bin/bash

conda create -n point-pillars-nvidia python=3.10
conda activate point-pillars-nvidia

conda install -y numpy==1.26.4 pyyaml==6.0.1 -c conda-forge
conda install -y open3d==0.18.0 -c open3d-admin
