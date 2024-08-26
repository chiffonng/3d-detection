#!/bin/bash
# https://docs.nvidia.com/tao/tao-toolkit/text/point_cloud/pointpillars.html#running-inference-on-the-pointpillars-model
pointpillars inference \
-e /workspace/specs/pointpillars_inference.yaml \
--key tlt_encode \
--results_dir /workspace/results
