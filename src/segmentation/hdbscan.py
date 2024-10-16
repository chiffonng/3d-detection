"""Apply HDBSCAN clustering to a point cloud."""

import logging
import sys
import open3d as o3d
import matplotlib.pyplot as plt
import numpy as np

from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.utils import resample

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


def apply_hdbscan(
    pcd: np.ndarray, min_cluster_size: int = 60, min_samples: int = 15
) -> np.ndarray:
    """Apply HDBSCAN clustering to the point cloud data.

    Args:
        pcd (np.ndarray): The point cloud data.
        min_cluster_size (int): Minimum size for a cluster to be considered valid.
        min_samples (int): Minimum number of points for a core point.

    Returns:
        np.ndarray: An array of labels for each point in the point cloud.
    """
    logger.info(
        f"Starting HDBSCAN clustering with min_cluster_size={min_cluster_size}, min_samples={min_samples}"
    )

    # Normalize the data for clustering
    scaler = StandardScaler()
    pcd_scaled = scaler.fit_transform(pcd)

    # Apply HDBSCAN with parallel processing
    hdb_clusterer = HDBSCAN(
        min_cluster_size=min_cluster_size, min_samples=min_samples, n_jobs=-1
    )
    labels = hdb_clusterer.fit_predict(pcd_scaled)
    num_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    num_noise = list(labels).count(-1)

    logger.info(
        f"HDBSCAN clustering complete. Found {num_clusters} clusters and {num_noise} noise points."
    )
    return labels


def main(file_path: str, do_subset: bool = True, n_samples: int = 50000):
    """Main function to load point cloud, apply HDBSCAN clustering, and visualize the results.

    Args:
        file_path (str): Path to the point cloud file.
        do_subset (bool): Whether to take a subset of the point cloud for testing.
        n_samples (int): Number of samples to take if subset is True.
    """
    # Load the point cloud
    pcd = o3d.io.read_point_cloud(file_path)
    logger.info(f"Loaded point cloud with dimensions: {np.asarray(pcd.points).shape}")

    # Subset for faster testing
    points = np.asarray(pcd.points)
    if do_subset:
        logger.info(
            f"Taking a subset of {n_samples} points from the point cloud for testing..."
        )
        points = resample(points, n_samples=n_samples)

    # Apply HDBSCAN on the subset
    labels = apply_hdbscan(points)

    # #! Avoid memory issues by visualizing in chunks. Currently not working since Open3D cannot visualize large point clouds.
    # logger.info("Assigning colors to clusters for visualization...")
    # max_label = max(labels)
    # colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
    # colors[labels < 0] = [0, 0, 0, 1]

    # # Assign colors to Open3D point cloud in smaller batches
    # pcd_subset = o3d.geometry.PointCloud()
    # pcd_subset.points = o3d.utility.Vector3dVector(points)
    # pcd_subset.colors = o3d.utility.Vector3dVector(colors[:, :3])

    # # Visualize the result
    # logger.info("Visualizing the point cloud with clusters...")
    # o3d.visualization.draw_geometries([pcd_subset])

    return labels


if __name__ == "__main__":
    main("data/pc1.prc.ply", do_subset=True)
