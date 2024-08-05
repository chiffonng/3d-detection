Detect cars from point clouds using [PointPillarNet from NVIDIA](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/pointpillarnet)

## TODOS

- [ ] Use trainable [PointPillarNet](https://catalog.ngc.nvidia.com/orgs/nvidia/teams/tao/models/pointpillarnet) on NGC

## Setup (UNDER CONSTRUCTION)

Check hardware requirements for [TAO Toolkit](https://docs.nvidia.com/tao/tao-toolkit/text/tao_toolkit_quick_start_guide.html#requirements)

Run this script to check for software requirements:

```bash
bash setup.sh
```

### Docker

Build the Docker image

```bash
docker build -t PointPillarNet docker/
```

Run the Docker container with active changes

```bash
docker run -it --rm PointPillarNet
-v $(pwd)/data:/workspace/data
-v $(pwd):/workspace/
--gpus all
```

## Data

Place the raw data in the "data" directory. The data should be in the form of a PLY file.

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

## Train & Fine-tune (UNDER CONSTRUCTION)

```bash
pointpillarnet train
-e /path/to/experiment/spec.txt
-r /path/to/experiment/results
-k $KEY
```

## Linting and Formatting

This repo uses [Ruff](https://docs.astral.sh/ruff/) for both linting and formatting Python code. Running `pre-commit` hook on staged files before committing is recommended.

```bash
pip install -r requirements.txt
pre-commit install
pre-commit run --all-files
```

Docstrings (Google convention) for functions and classes are enforced by Ruff via `pydocstyle`.
