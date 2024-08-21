Detect cars from point clouds using [PointPillarNet from NVIDIA](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/pointpillarnet). All steps produced here are based on NVIDIA's [PointPillars guide](https://docs.nvidia.com/tao/tao-toolkit/text/point_cloud/pointpillars.html).

## TODOS

- [ ] Split point cloud data into sensible scenes
- [ ] Run inference on given data

## Setup

Check hardware requirements for [TAO Toolkit](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#requirements)

Run this script to check for software requirements, build the Docker image, and create a container.

```bash
bash setup.sh
```

## Data

Place the raw data in the "data" directory. The data should be in the form of a PLY file.

```bash
python3 src/process_data.py data/raw.ply
```

converts "data/raw.ply" to KITTI format compatible with PointPillarNet [as required](https://docs.nvidia.com/tao/tao-toolkit/text/point_cloud/pointpillars.html#preparing-the-dataset)

Otherwise, we can provide more arguments to process_data.py

```bash
python3 src/process_data.py --help
```

For example, to force processing a different file named "file.ply" and limit the number of points per scene to 120000:

```bash
python3 src/process_data.py file.ply -f --points_per_scene 120000
```

## INFERENCE (UNDER CONSTRUCTION)

```bash
docker run -it --rm --name tao_toolkit \
  -v "$(pwd):/workspace/" \
  -v "$(pwd)/data:/workspace/data" \
  -v "$(pwd)/models:/workspace/models" \
  --gpus all \
  --ipc=host \
  --ulimit memlock=-1 \
  tao_toolkit \
  pointpillars evaluate \
  -e /workspace/specs/pointpillars_inference.yaml \
  -k tlt_encode \
  -r results \
```

## Linting and Formatting

This repo uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting Python code. Running `pre-commit` hook on staged files before committing is recommended.

```bash
pip install -r requirements.txt
pre-commit install
pre-commit run --all-files
```

Docstrings (Google convention) for functions and classes are enforced by Ruff via `pydocstyle`.
