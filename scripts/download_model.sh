#!/bin/bash

source ./utils.sh

# Check that wget and unzip are installed
if ! [ -x "$(command -v wget)" ]; then
  error "wget is not installed. See other downloading options on
  https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/pointpillarnet" >&2
  exit 1
fi

# Check the argument
if [ "$1" == "deploy" ] || [ "$1" == "inference" ] || [ "$1" == "test" ]; then
  MODEL_URL="https://api.ngc.nvidia.com/v2/models/nvidia/tao/pointpillarnet/versions/deployable_v1.0/zip"
  MODEL_NAME="pointpillarnet_deployable.zip"
else
  MODEL_URL="https://api.ngc.nvidia.com/v2/models/nvidia/tao/pointpillarnet/versions/trainable_v1.1/zip"
  MODEL_NAME="pointpillarnet_trainable.zip"
fi

# Download the model
wget --content-disposition $MODEL_URL -O $MODEL_NAME
unzip $MODEL_NAME -d models
rm $MODEL_NAME
