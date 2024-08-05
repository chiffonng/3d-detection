FROM nvcr.io/nvidia/tao/tao-toolkit:5.3.0-pyt

# Set the environment variables
ENV DATA_DIR="/data"
ENV MODELS_DIR="/pretrained_models"
ENV KEY=tlt_encode

# Working directory
RUN mkdir -p /workspace
WORKDIR /workspace

# Install dependencies
COPY requirements.txt /workspace/
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install -r requirements.txt

# Copy the source code to workspace
COPY . /workspace/

# Run the scripts
RUN chmod +x /workspace/scripts/*.sh

# Define mount point for data and models inside workspace
VOLUME ["${DATA_DIR}", "${MODELS_DIR}"]

# Set the entrypoint
ENTRYPOINT ["bash", "/scripts/docker_entrypoint.sh"]
