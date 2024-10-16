"""Process data for point cloud segmentation tasks."""

import logging
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def read_ply_file(
    file_path: str | Path,
    dtype: np.dtype = np.float32,
    num_features: int = 4,
) -> np.ndarray:
    """Read a PLY file (binary format), infer headers, number of points, and data type, and return the point cloud with 4 features: x, y, z, and intensity.

    Args:
        file_path (str or Path): The path to the PLY file.
        dtype (np.dtype, optional): The data type to use for the point cloud. Defaults to np.float32.
        num_features (int, optional): The number of features per point. Defaults to 4.

    Returns:
        np.ndarray: The point cloud with shape (N, 4).
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    elif file_path.suffix != ".ply":
        raise ValueError(f"Invalid file format. Expected .ply, got {file_path.suffix}")

    with open(file_path, "rb") as f:
        # Read the header
        header = b""
        while b"end_header" not in header:
            header += f.read(1)

        header = header.decode("ascii").strip()

        # Find the number of points and the data type from the header
        num_points = 0

        for line in header.splitlines():
            if line.startswith("element vertex"):
                num_points = int(line.split()[2])
            elif line.startswith("property"):
                dtype_str = line.split()[1]
                if dtype_str in ["float", "float32"]:
                    dtype = np.float32
                elif dtype_str in ["double", "float64"]:
                    dtype = np.float64

        if num_points == 0:
            raise ValueError(
                "Failed to determine the number of points from the PLY header."
            )

        # Read the data using inferred dtype
        pcd = np.fromfile(file_path, dtype=dtype, offset=len(header) + 1)

        # Reshape to (N, num_features)
        if len(pcd) % num_features != 0:
            raise ValueError(
                f"Number of points is not divisible by the number of features. Make sure {num_features} is correct: {num_points} % {num_features} = 0"
            )
        else:
            pcd = pcd.reshape((-1, num_features))

        logger.info(
            f"📦 Loaded {num_points} points from '{file_path}' Dimensions: {pcd.shape}"
        )

        return pcd
