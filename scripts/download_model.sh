#!/bin/bash

source ./utils.sh

# Check that wget and unzip are installed
if ! [ -x "$(command -v wget)" ]; then
  error "wget is not installed. See other download options on
  https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/pointpillarnet" >&2
  exit 1
fi

if [ "$1" == "train" ] || [ "$1" == "fine-tune" ] || [ "$1" == "t" ] || [ "$1" == "ft" ]; then
  MODEL_URL="https://api.ngc.nvidia.com/v2/models/nvidia/tao/pointpillarnet/versions/trainable_v1.1/zip"
  MODEL_NAME="pointpillarnet_trainable.zip"
else
  MODEL_URL="https://api.ngc.nvidia.com/v2/models/nvidia/tao/pointpillarnet/versions/deployable_v1.0/zip"
  MODEL_NAME="pointpillarnet_deployable.zip"
fi

# Download the model
wget --content-disposition $MODEL_URL -O $MODEL_NAME
unzip $MODEL_NAME -d models
rm $MODEL_NAME
