#! /bin/bash
# Copied and modified from NVIDIA TAO Toolkit repository.
# COPYRIGHT 2024 NVIDIA Corporation. These scripts are provided on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

success_code=0 # 1 for failure
set -e

chmod +x scripts/*.sh
source ./scripts/utils.sh

function check_tao_hardware_requirements() {
    warning "Checking hardware requirements.
    This check is not comprehensive, you should verify by checking your hardware specifications.
    Mimimum requirements are as listed here:
    https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#hardware-requirements"

    # Check system RAM
    system_ram=$(free -g | awk '/^Mem:/{print $2}')
    if (( system_ram < 8 )); then
        error "At least 8 GB system RAM is required."
        return 1
    fi

    # Check CPU cores
    cpu_cores=$(nproc)
    if (( cpu_cores < 8 )); then
        error "At least 8 CPU cores are required."
    fi

    # Check SSD space
    ssd_space=$(df -BG --output=avail / | tail -n 1 | tr -d 'G')
    if (( ssd_space < 100 )); then
        error "At least 100 GB of SSD space is required."
    fi

    # If nvidia-smi is not available, skip this check
    if ! command -v nvidia-smi >/dev/null; then
        warning "nvidia-smi not found. Skipping GPU automatic check."
    else
        # Check GPU RAM
        gpu_ram=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n 1)
        if (( gpu_ram < 4 )); then
            error "At least 4 GB GPU RAM is required."
        fi
        # Check if at least 1 NVIDIA GPU is available
        nvidia_gpu_count=$(nvidia-smi --query-gpu=count --format=csv,noheader)
        if (( nvidia_gpu_count < 1 )); then
            error "At least 1 NVIDIA GPU is required."
        fi
    fi

    # If all checks pass, return 0, otherwise don't return anything.
    return 0
}


function check_tao_software_requirements() {

    info "Check software requirements"

    # Check OS, Ubuntu >= 20.04 is required.
    if [[ $OSTYPE != linux-gnu ]]; then
        error "Unsupported OS: $OSTYPE. Ubuntu >= 20.04 is required."
        return 1
    else
        if [[ -f /etc/os-release ]]; then
            os_name=$(grep "NAME" /etc/os-release | cut -d "=" -f 2 | tr -d '"')
            os_version=$(grep "VERSION_ID" /etc/os-release | cut -d "=" -f 2 | tr -d '"')
            # Take the first two characters of the version and turn into number. If it<20, return error
            if [ "$(echo "$os_version" | cut -d "." -f 1)" -lt 20 ]; then
                error "Unsupported OS: $os_name Ubuntu >= 20.04 is required."
                return 1
            else
                info "OS: $os_name"
            fi
        else
            error "Unsupported OS: $OSTYPE. Ubuntu >= 20.04 is required."
            return 1
        fi
    fi

    # Check GPU driver, version >= 535.xx is required.
    if ! command -v nvidia-smi >/dev/null; then
        error "NVIDIA driver not found. Please install NVIDIA driver.
        See: https://www.nvidia.com/download/index.aspx"
        return 1
    else
        driver_version=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader)
        driver_major_version=$(echo "$driver_version" | cut -d "." -f 1)
        if [[ $driver_major_version -lt 535 ]]; then
            error "Unsupported driver version: $driver_version. Driver version >= 535.xx is required."
            return 1
        else
            info "NVIDIA Driver version: $driver_version"
        fi
    fi

    # Check nvidia-container-toolkit.
    if ! command -v nvidia-container-toolkit >/dev/null; then
        error "nvidia-container-toolkit not found. Please install nvidia-container-toolkit here: https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html"
        return 1
    else
        nvidia_container_version=$(nvidia-container-toolkit --version | cut -d " " -f 6)
        nvidia_container_major_version=$(echo "$nvidia_container_version" | cut -d "." -f 1)
        nvidia_container_minor_version=$(echo "$nvidia_container_version" | cut -d "." -f 2)
        nvidia_container_patch_version=$(echo "$nvidia_container_version" | cut -d "." -f 3)

        # check if version (X.Y.Z) <= 1.3.1
        if [[ $nvidia_container_major_version -lt 1 || ($nvidia_container_major_version -eq 1 && $nvidia_container_minor_version -lt 3) || ($nvidia_container_major_version -eq 1 && $nvidia_container_minor_version -eq 3 && $nvidia_container_patch_version -lt 1) ]]; then
            error "Unsupported nvidia-container-toolkit version: $(nvidia-container-toolkit --version). Version >= 1.3.1 is required."
            return 1
        else
            info "$(nvidia-container-toolkit --version)"
        fi
    fi

    # Check python.
    if ! command -v python3 >/dev/null; then
        error "python3 not found"
        return 1
    else
        info "python3 found."
        # Check python version >3.7,<=3.10. Only check minor version.
        python_version=$(python3 --version | cut -d " " -f 2)
        python_minor_version=$(echo "$python_version" | cut -d "." -f 2)
        if [[ $python_minor_version -ge 7 && $python_minor_version -le 10 ]]; then
            info "Python version: $python_version"
        else
            warning "Unsupported python version: $python_version. Python version >3.7,<=3.10 is required."
        fi
    fi

    # Check pip.
    if ! command -v pip3 >/dev/null; then
        error "pip3 not found"
        return 1
    else
        info "pip3 found."
        # Check pip version >= 21.06
        pip_version=$(pip3 --version | cut -d " " -f 2)

        # Check if pip major version >21 and if it =21, then check for the minor version.
        if [[ $(echo "$pip_version" | cut -d "." -f 1) -gt 21 || ($(echo "$pip_version" | cut -d "." -f 1) -eq 21 && $(echo "$pip_version" | cut -d "." -f 2) -ge 6) ]]; then
            info "pip version: $pip_version"
        else
            warning "Version >= 21.06 is required. Upgrading pip..."
            pip3 install --upgrade pip
        fi
    fi

    # Check docker.
    docker_registry="nvcr.io"
    if ! command -v docker >/dev/null; then
        error "docker not found. Please install docker-ce"
        return 1
    else
        info "Docker found. Checking additional requirements for docker."
        if ! id -nG | grep -qw "docker"; then
            [[ $OSTYPE = darwin* ]] || error "To run Docker in rootless mode, you should add yourself to the docker group by running \"sudo usermod -a -G docker $(whoami)\"" && return 1
        fi
        if ! grep -q "nvcr.io" "$HOME"/.docker/config.json; then
            error "You should login to NGC container registry by running 'docker login -u \"\$oauthtoken\" ${docker_registry}'."
            error "For more information, please refer to step 3 in this guide: https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#launcher-cli
            OR a dedicated NGC Guide
            https://docs.nvidia.com/ngc/gpu-cloud/ngc-user-guide/index.html#ngc-api-keys"
            return 1
        fi
    fi

    # Successfully checked all dependencies.
    return 0
}

# Print EULA prompt.
function prompt_tao_toolkit_eula() {
    tao_toolkit_license_text="
    By using the TAO Toolkit, you accept the terms and conditions of this license:
    https://developer.nvidia.com/tao-toolkit-software-license-agreement"
    echo "$tao_toolkit_license_text"
    read -rp  "Would you like to continue? (y/n): " confirm
    if [[ $confirm == [yY] || $confirm == [yY][eE][sS] ]]; then
        info "EULA accepted."
        return 0
    else
        error "EULA not accepted. Don't start installation."
        return 1
    fi
}

function create_folder_structures() {
  mkdir -p data
  mkdir -p models
  mkdir -p results
}

function setup_docker() {
  # If there is no image, build the image.
  if ! docker images -a | grep -q "tao_toolkit"; then
    info "Building docker image..."
    docker build -t tao_toolkit -f docker/Dockerfile .
  fi
  info "Running docker container temporarily. Use 'exit' to stop the container."
  docker run -it --rm --name tao_toolkit \
  -v "$(pwd):/workspace/" \
  -v "$(pwd)/data:/workspace/data" \
  -v "$(pwd)/models:/workspace/models" \
  -v "$(pwd)/results:/workspace/results" \
  --gpus all \
  --ipc=host \
  --ulimit memlock=-1 \
  tao_toolkit
}

# Main function to run quick start.
function main() {
    check_tao_hardware_requirements
    check_tao_software_requirements
    requirements_status=$?

    if [[ $requirements_status -eq $success_code ]]; then
        info "Requirements satisfied"
    fi
        prompt_tao_toolkit_eula
        eula_status=$?

    if [[ $eula_status -eq $success_code ]]; then
        info "Create folder structure..."
        create_folder_structures
        setup_docker
    fi
}

main
