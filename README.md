Detect cars from point clouds using PointPillarNet from NVIDIA

Current setup requires TAO Launcher CLI

## TODOS

- [ ] Only pull PointPillarNet from NVIDIA
- [ ] Use trainable [PointPillarNet](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/pointpillarnet) on NGC

## Linting and Formatting

This repo uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting Python code. Running `pre-commit` hook on staged files before committing is recommended.

```bash
pip install -r requirements.txt
pre-commit install
pre-commit run --all-files
```

Docstrings (Google convention) for functions and classes are enforced by Ruff via `pydocstyle`.
