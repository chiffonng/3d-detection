"""Turn raw data into KITTI-formatted data, compatible with NVIDIA PointPillars.

See convert_to_kitti_format() for more details.
"""

import argparse as ap
import sys
import warnings
from pathlib import Path
from typing import List, Optional

sys.path.append(str(Path(__file__).resolve().parents[1]))

import numpy as np
from tqdm import tqdm

from src.utils import get_absolute_path, has_file_ext

KITTI_DIRECTORIES = [
    "data/train/lidar",
    "data/train/label",
    "data/val/lidar",
    "data/val/label",
]


def create_kitti_directories() -> List[Path]:
    """Create the KITTI-formatted directories.

    data/
    ├── train/
    │   ├── lidar/
    │   │   ├── 0.bin
    │   │   ├── 1.bin
    │   ├── label/
    │   │   ├── 0.txt
    │   │   ├── 1.txt
    ├── val/
    │   ├── lidar/
    │   │   ├── 0.bin
    │   │   ├── 1.bin
    │   ├── label/

    Source: https://docs.nvidia.com/tao/tao-toolkit/text/point_cloud/pointpillars.html

    Returns:
        List[str | Path]: List of KITTI directories created
    """
    created_dirs = []
    for directory in KITTI_DIRECTORIES:
        directory = get_absolute_path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        created_dirs.append(directory)
    return created_dirs


def is_any_kitti_dir_empty(directory: Optional[str] = None) -> bool:
    """Check if none of the KITTI-formatted directories are empty. Or check if a specific KITTI directory is empty.

    - lidar/ must have at least one .bin file.

    Args:
        directory (Optional[str]): The directory (compared to project root) to check. If None, check all KITTI directories.

    Returns:
        bool: Whether the KITTI-formatted directories are empty
    """
    if directory:
        directory = get_absolute_path(directory)
        return has_file_ext(directory, ".bin")
    else:
        for directory in KITTI_DIRECTORIES:
            # Check if lidar/ has at least one .bin file
            if "lidar" in directory.name and has_file_ext(directory, ".bin"):
                return True
            # // Check if label/ has at least one .txt file
            # // elif "label" in directory.name and has_file_ext(directory, ".txt"):
            # //     return True
        return False


def read_ply_file(
    file_path: str | Path,
    dtype: Optional[np.dtype] = np.float32,
    num_points: Optional[int] = None,
) -> np.ndarray:
    """Read a PLY file (binary format), infer headers, number of points, and data type, and return the point cloud with 4 features: x, y, z, and intensity.

    Args:
        file_path (str | Path): The path to the PLY file.
        dtype (np.dtype, optional): The data type to use for the point cloud. Defaults to np.float32.
        num_points (int, optional): The known number of points in the point cloud. Defaults to None.

    Returns:
        np.ndarray: The point cloud with shape (N, 4).
    """
    file_path = Path(file_path)

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

        if pcd.shape[0] != num_points * 4:
            raise ValueError(
                f"Expected {num_points} points with 4 features each, got {pcd.shape[0]}."
            )

        # Reshape to (N, 4) assuming 4 features per point
        return pcd.reshape((-1, 4))


def verify_point_cloud(pcd: np.ndarray) -> None:
    """Verify the point cloud data.

    Args:
        pcd (np.ndarray): The point cloud data.
    """
    # Check the shape
    assert pcd.shape[1] == 4, f"Expected 4 features, got {pcd.shape[1]}."

    # Check the ranges of intensity, the last feature
    intensity = pcd[:, -1]
    assert np.all(
        (intensity >= 0) & (intensity <= 1)
    ), "Intensity should be in the range [0, 1]."


def _validate_io_paths(file_path: str, output_dir: str) -> None:
    """Validate the file path and output directory.

    Args:
        file_path (str): The file path to the raw point cloud.
        output_dir (str): The directory to save the KITTI-formatted data.

    Raises:
        FileNotFoundError: When file_path or output_dir does not exist.
        ValueError: When file_path is not a file or output_dir is not a KITTI directory.
    """
    # Validate the file path
    file_path = get_absolute_path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist.")
    elif not file_path.is_file():
        raise ValueError(f"{file_path} is not a file.")

    # Validate the output directory
    if output_dir not in KITTI_DIRECTORIES:
        raise ValueError(f"{output_dir} is not a valid KITTI directory.")
    elif not Path(output_dir).exists():
        create_kitti_directories()


def convert_to_kitti_format(
    input_file: str, points_per_scene: int, output_dir: str
) -> None:
    """Convert a point cloud to KITTI-formatted data.

    Each .bin has shape (N, 4), where N is the number of points in the frame, and the columns are [x, y, z, intensity], where intensity is rotation around the z-axis. Each .txt has shape (N, 8), where N is the number of objects in the frame, and the columns are [type, truncated, occluded, alpha, bbox, dimensions, location, rotation].

    Source: https://github.com/bostondiditeam/kitti/blob/master/resources/devkit_object/readme.txt

    Args:
        input_file (str): File path to the raw point cloud, compared to the project root.
        points_per_scene (int): Desired number of points per frame.
        output_dir (str): Directory to save the KITTI-formatted data, compared to project root.

    Raises:
        FileNotFoundError: When file_path or output_dir does not exist.
        ValueError: When file_path is not a file or output_dir is not a KITTI directory.
        UserWarning: When points_per_scene is larger than the number of points in the point cloud.
    """
    _validate_io_paths(input_file, output_dir)

    # Load the point cloud data
    pcd = read_ply_file(input_file)
    verify_point_cloud(pcd)

    # Split the point cloud into frames
    if points_per_scene > pcd.shape[0]:
        warnings.warn(
            f"points_per_scene ({points_per_scene} > {pcd.shape[0]}, the number of points. Using all points.",
            UserWarning,
        )
    points_per_scene = min(points_per_scene, pcd.shape[0])
    num_frames = pcd.shape[0] // points_per_scene
    frames = np.array_split(pcd, num_frames)

    # Save each frame as a .bin file
    for i, frame in enumerate(
        tqdm(frames, desc="⏳ Converting to KITTI-formatted data", unit="frames")
    ):
        frame.tofile(f"{output_dir}/{i}.bin")


def main():
    """Parse command-line arguments and convert raw data to KITTI-formatted data."""
    parser = ap.ArgumentParser(description="Convert raw data to KITTI-formatted data.")
    parser.add_argument(
        "filepath",  # Required positional argument
        type=str,
        help="file path to the raw point cloud, compared to the project root.",
    )
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        default="data/val/lidar",
        help="directory to save the KITTI-formatted data, compared to the project root.",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        default=False,
        help="whether to overwrite the existing KITTI-formatted data with new data. Default: False.",
    )
    parser.add_argument(
        "--points_per_scene",
        type=int,
        default=100000,
        help="desired number of points per frame/scene. Default: 100000.",
    )

    args = parser.parse_args()

    if args.force or is_any_kitti_dir_empty():
        convert_to_kitti_format(
            input_file=args.filepath,
            points_per_scene=args.points_per_scene,
            output_dir=args.output_dir,
        )
    else:
        warnings.warn(
            "KITTI-formatted directories already exists. Use -f or --force to overwrite.",
            UserWarning,
        )


if __name__ == "__main__":
    main()
