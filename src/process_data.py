"""Turn raw data into KITTI-formatted data, compatible with NVIDIA PointPillars."""

from pathlib import Path

import numpy as np
import open3d as o3d


def convert_to_kitti_format(
    file_path: str | Path,
    output_dir: str | Path | None = "data/val/lidar",
    points_per_scene: int | None = 100000,
    seed: int | None = 42,
) -> None:
    """Convert a point cloud to KITTI-formatted data.

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

    Each .bin has shape (N, 4), where N is the number of points in the frame, and the columns are [x, y, z, intensity], where intensity is rotation around the z-axis. Each .txt has shape (N, 8), where N is the number of objects in the frame, and the columns are [type, truncated, occluded, alpha, bbox, dimensions, location, rotation].

    More references:
    - https://docs.nvidia.com/tao/tao-toolkit/text/point_cloud/pointpillars.html
    - https://github.com/bostondiditeam/kitti/blob/master/resources/devkit_object/readme.txt

    Args:
        file_path (str | Path): File path to the raw point cloud.
        output_dir (str or Path, optional): Directory to save the KITTI-formatted data. Defaults to "data/val/lidar".
        points_per_scene (int, optional): Desired number of points per frame. Defaults to 100000.
        seed (int, optional): Seed for NumPy random number generator. Defaults to 42.

    Raises:
        FileNotFoundError: When file_path or output_dir does not exist.
        ValueError: When file_path is not a file or output_dir is not a directory.
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} does not exist.")
    elif not file_path.is_file():
        raise ValueError(f"{file_path} is not a file.")

    if isinstance(output_dir, str):
        output_dir = Path(output_dir)
    if not output_dir.exists():
        raise FileNotFoundError(f"{output_dir} does not exist.")
    elif not output_dir.is_dir():
        raise ValueError(f"{output_dir} is not a directory.")

    # Load the point cloud
    pcd = o3d.io.read_point_cloud(file_path)
    points = np.asarray(pcd.points)

    # Split the point cloud into frames
    points_per_scene = min(points_per_scene, points.shape[0])
    num_frames = points.shape[0] // points_per_scene
    frames = np.array_split(points, num_frames)

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    for i, frame in enumerate(frames):
        # Add intensity to each frame
        # TODO: Remove when using real data
        rng = np.random.default_rng(seed=seed)
        intensity = rng.uniform(0, 1, size=(frame.shape[0], 1))
        frame = np.hstack([frame, intensity])

        # Save each frame to a .bin file
        frame.tofile(f"{output_dir}/{i}.bin")


convert_to_kitti_format("data/raw.ply")
