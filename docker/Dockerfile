# https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/containers/tao-toolkit
FROM nvcr.io/nvidia/tao/tao-toolkit:5.5.0-pyt

# Set the environment variables
ENV DATA_DIR="/workspace/data"
ENV MODELS_DIR="/workspace/models"
ENV RESULTS_DIR="/workspace/results"
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
# RUN chmod +x /workspace/scripts/*.sh

# Define mount point for data and models inside container
VOLUME ["${DATA_DIR}", "${MODELS_DIR}", "${RESULTS_DIR}"]

# Set the entrypoint
ENTRYPOINT ["bash"]
