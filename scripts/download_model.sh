#!/bin/bash

# shellcheck source=./scripts/utils.sh
source ./scripts/utils.sh

# Check that wget and unzip are installed
if ! [ -x "$(command -v wget)" ]; then
  error "wget is not installed. See other download options on
  https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/pointpillarnet" >&2
  exit 1
fi

if [ "$1" == "train" ] || [ "$1" == "fine-tune" ] || [ "$1" == "t" ] || [ "$1" == "ft" ]; then
  MODEL_URL="https://api.ngc.nvidia.com/v2/models/nvidia/tao/pointpillarnet/versions/trainable_v1.1/zip"
  MODEL_ZIP="pointpillarnet_trainable.zip"
  MODEL_NAME="pointpillarnet_trainable.tlt"
else
  MODEL_URL="https://api.ngc.nvidia.com/v2/models/nvidia/tao/pointpillarnet/versions/deployable_v1.0/zip"
  MODEL_ZIP="pointpillarnet_deployable.zip"
  MODEL_NAME="pointpillarnet_deployable.etlt"
fi

# Check if the model already exists inside "models" folder
if [ -d "models/$MODEL_NAME" ]; then
  warning "Model already exists in models folder. Skipping download."
  exit 0
fi

# Download the model
info "Downloading pre-trained model..."
wget --content-disposition $MODEL_URL -O $MODEL_ZIP
unzip $MODEL_ZIP -d models
rm $MODEL_ZIP
