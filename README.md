# 3D Object Detection & Semantic Segmentation

`src/detection`: Detect cars from point clouds using [PointPillarNet from NVIDIA](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/pointpillarnet), TAO Toolkit 5.3 with Pytorch. Most steps produced here are based on NVIDIA's [PointPillars guide](https://docs.nvidia.com/tao/tao-toolkit/text/cv_finetuning/pytorch/point_cloud/pointpillars.html).
`src/segmentation`: Codebase for semantic segmentation of point clouds, using HDBSCAN clustering, and (planned) PointNet++.

## Setup

### Detection with PointPillarNet

Check hardware requirements for [TAO Toolkit](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#requirements)

Run this script to check for software requirements, build the Docker image, and create a container. The interactive shell will be available in the container.

```bash
bash setup.sh
```

By default, the script downloads deployable model from NGC for inference. To switch to trainable model, see the comment "#!" in the script.

### Semantic Segmentation

Requires Python >= 3.10 for better data type hints.

```bash
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements-seg.txt
```

## Data

Place the raw data in the "data" directory. The data should be in the form of a PLY file.

```bash
python3 src/detection/process_data.py data/raw.ply
```

converts "data/raw.ply" to KITTI format compatible with PointPillarNet [as required](https://docs.nvidia.com/tao/tao-toolkit/text/point_cloud/pointpillars.html#preparing-the-dataset)

Otherwise, we can provide more arguments to process_data.py

```bash
python3 src/detection/process_data.py --help
```

For example, to force processing a different file named "file.ply" and limit the number of points per scene to 120000:

```bash
python3 src/detection/process_data.py data/file.ply -f --points_per_scene 120000
```

## INFERENCE

Currently inference with PointPillarNet is NOT running because there is no `.pth` checkpoint available, which is required in the `run_inference.sh` script. The script is provided for reference.

```bash
bash scripts/run_inference.sh
```

## Linting and Formatting

This repo uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting Python code. Running `pre-commit` hook on staged files before committing is recommended.

```bash
pre-commit install
pre-commit run --all-files
```

Docstrings (Google convention) for functions and classes are enforced by Ruff via `pydocstyle`. This can be changed or disabled in `ruff.toml`.
