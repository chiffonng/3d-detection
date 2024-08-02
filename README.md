Detect cars from point clouds using PointPillarNet from NVIDIA

Current setup requires TAO Launcher CLI

## TODOS

- [ ] Only pull PointPillarNet from NVIDIA
- [ ] Use trainable [PointPillarNet](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/pointpillarnet) on NGC

## Setup

## Process data

```bash
python3 src/process_data.py data/raw.ply
```

converts "data/raw.ply" to KITTI format compatible with PointPillarNet

Otherwise, we can provide more arguments to process_data.py

```bash
python3 src/process_data.py --help
```

For example, to force processing a different file named "file.ply" and limit the number of points per scene to 120000:

```bash
python3 src/process_data.py file.ply -f --points_per_scene 120000
```

## Linting and Formatting

This repo uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting Python code. Running `pre-commit` hook on staged files before committing is recommended.

```bash
pip install -r requirements.txt
pre-commit install
pre-commit run --all-files
```

Docstrings (Google convention) for functions and classes are enforced by Ruff via `pydocstyle`.
