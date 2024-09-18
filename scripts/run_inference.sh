#!/bin/bash
# v5.3: https://docs.nvidia.com/tao/archive/5.3.0/text/point_cloud/pointpillars.html#running-inference-on-the-pointpillars-model
# New: https://docs.nvidia.com/tao/tao-toolkit/text/cv_finetuning/pytorch/point_cloud/pointpillars.html#running-inference-on-the-pointpillars-model
pointpillars inference \
-e /workspace/specs/pointpillars_inference.yaml \
--key tlt_encode \
--results_dir /workspace/results
