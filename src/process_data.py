"""Turn raw data into KITTI-formatted data, compatible with NVIDIA PointPillars."""

import argparse as ap
from pathlib import Path
from typing import List, Optional

import numpy as np
import open3d as o3d
from tqdm import tqdm

# root/src/process_data.py
PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
    kitti_directories = [
        "data/train/lidar",
        "data/train/label",
        "data/val/lidar",
        "data/val/label",
    ]
    created_dirs = []
    for directory in kitti_directories:
        directory = PROJECT_ROOT / directory
        directory.mkdir(parents=True, exist_ok=True)
        created_dirs.append(directory)
    return created_dirs


def has_file(directory: Path, file_extension: str) -> bool:
    """Check if a directory contains at least one file with the given extension.

    Args:
        directory (Path): The directory to check.
        file_extension (str): The file extension to look for.

    Returns:
        bool: True if the directory is empty, False otherwise.
    """
    return not any(directory.glob(f"*{file_extension}"))


def is_any_kitti_dir_empty(directory: Optional[str]) -> bool:
    """Check if none of the KITTI-formatted directories are empty. Or check if a specific KITTI directory is empty.

    - lidar/ must have at least one .bin file.

    Args:
        directory (Optional[str]): The directory to check. If None, check all KITTI directories.

    Returns:
        bool: Whether the KITTI-formatted directories are empty
    """
    if directory:
        directory = PROJECT_ROOT / dir
        return has_file(directory, ".bin")
    else:
        kitti_directories = create_kitti_directories()
        for directory in kitti_directories:
            # Check if lidar/ has at least one .bin file
            if "lidar" in directory.name and has_file(directory, ".bin"):
                return True
        return False


def convert_to_kitti_format(
    file_path: str,
    points_per_scene: int,
    seed: int,
    output_dir: str,
) -> None:
    """Convert a point cloud to KITTI-formatted data.

    Each .bin has shape (N, 4), where N is the number of points in the frame, and the columns are [x, y, z, intensity], where intensity is rotation around the z-axis. Each .txt has shape (N, 8), where N is the number of objects in the frame, and the columns are [type, truncated, occluded, alpha, bbox, dimensions, location, rotation].

    Source: https://github.com/bostondiditeam/kitti/blob/master/resources/devkit_object/readme.txt

    Args:
        file_path (str): File path to the raw point cloud, compared to the project root.
        points_per_scene (int): Desired number of points per frame.
        seed (int, optional): Seed for NumPy random number generator.
        output_dir (str): Directory to save the KITTI-formatted data, compared to project root.

    Raises:
        FileNotFoundError: When file_path does not exist.
        ValueError: When file_path is not a file or output_dir is not a directory.
    """
    # Get the absolute paths
    file_path = PROJECT_ROOT / file_path
    output_dir = PROJECT_ROOT / output_dir

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist.")
    elif not file_path.is_file():
        raise ValueError(f"{file_path} is not a file.")

    if not output_dir.exists():
        raise FileNotFoundError(f"{output_dir} does not exist.")
    elif not output_dir.is_dir():
        raise ValueError(f"{output_dir} is not a directory.")

    # Load the point cloud
    pcd = o3d.io.read_point_cloud(str(file_path))
    points = np.asarray(pcd.points)

    # Split the point cloud into frames
    points_per_scene = min(points_per_scene, points.shape[0])
    num_frames = points.shape[0] // points_per_scene
    frames = np.array_split(points, num_frames)

    for i, frame in enumerate(
        tqdm(frames, desc="⏳ Converting to KITTI-formatted data", unit="frames")
    ):
        # Add intensity to each frame
        # TODO: Remove when using real data
        rng = np.random.default_rng(seed=seed)
        intensity = rng.random((frame.shape[0], 1))
        frame_with_intensity = np.hstack([frame, intensity])

        # Save each frame to a .bin file
        frame_with_intensity.tofile(f"{output_dir}/{i}.bin")


def main():
    """Parse command-line arguments and convert raw data to KITTI-formatted data."""
    parser = ap.ArgumentParser(description="Convert raw data to KITTI-formatted data.")
    parser.add_argument(
        "filepath",  # Required positional argument
        "f",
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
        help="whether to overwrite the existing KITTI-formatted data with new data.",
    )
    parser.add_argument(
        "--points_per_scene",
        type=int,
        default=100000,
        help="desired number of points per frame/scene.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="seed for NumPy random number generator.",
    )

    args = parser.parse_args()

    if args.force or is_any_kitti_dir_empty():
        convert_to_kitti_format(
            args.filepath,
            points_per_scene=args.points_per_scene,
            seed=args.seed,
            output_dir=args.output_dir,
        )
    else:
        print(
            "KITTI-formatted directories already exists. Use -f or --force to overwrite."
        )


if __name__ == "__main__":
    main()
