"""Apply HDBSCAN clustering to a point cloud and save the clustered point cloud.

1. Load the point cloud from a file.
2. Downsample the point cloud using voxel grid filtering.
3. Apply HDBSCAN clustering to the downsampled point cloud data.
4. Propagate the labels from the downsampled points to the original point cloud using nearest neighbors.
5. Save the clustered point cloud to a file in parallel.
"""

import logging

import open3d as o3d
from open3d import PointCloud  # for type hinting
from sklearn.cluster import HDBSCAN
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import StandardScaler
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler("logs/hdbscan.log"))


def load_point_cloud(file_path: str) -> PointCloud:
    """Load a point cloud from a file."""
    logger.info(f"Loading point cloud from {file_path}")
    return o3d.io.read_point_cloud(file_path)


def downsample_point_cloud(
    pcd: PointCloud, voxel_size: float
) -> o3d.geometry.PointCloud:
    """Downsample the point cloud using voxel grid filtering."""
    logger.info(f"Downsampling point cloud with voxel size {voxel_size}")
    return pcd.voxel_down_sample(voxel_size=voxel_size)


def apply_hdbscan(pcd: PointCloud, min_cluster_size: int, min_samples: int) -> list:
    """Apply HDBSCAN clustering directly to the point cloud data using Open3D's accessors."""
    logger.info(
        f"Clustering with HDBSCAN (min_cluster_size={min_cluster_size}, min_samples={min_samples})"
    )
    points = pcd.points  # Get direct reference without converting to a NumPy array

    # Standardize the point cloud data
    scaler = StandardScaler()
    scaled_points = scaler.fit_transform(points)

    # Apply HDBSCAN
    hdb_clusterer = HDBSCAN(
        min_cluster_size=min_cluster_size, min_samples=min_samples, n_jobs=-1
    )
    labels = hdb_clusterer.fit_predict(scaled_points)

    logger.info(
        f"Clustering complete: found {len(set(labels)) - (1 if -1 in labels else 0)} clusters"
    )
    return labels


def propagate_labels_to_o3d(
    original_pcd: PointCloud,
    downsampled_pcd: PointCloud,
    downsampled_labels: list[int],
) -> list[int]:
    """Propagate labels from the downsampled point cloud to the original point cloud."""
    logger.info("Propagating labels using nearest neighbors")
    original_points = original_pcd.points

    # Fit nearest neighbors
    nn = NearestNeighbors(n_neighbors=1, n_jobs=-1).fit(downsampled_pcd.points)
    _, indices = nn.kneighbors(original_points)

    # Use the nearest label
    return [downsampled_labels[i[0]] for i in indices]


def save_clustered_pcd_ply(
    pcd: PointCloud,
    labels: list,
    output_path: str,
    chunk_size: int = 10000,
):
    """Save the clustered point cloud to a PLY file."""
    logger.info(f"Saving clustered point cloud to {output_path}")
    num_points = len(pcd.points)
    with open(output_path, "w") as f:
        f.write(f"ply\nformat ascii 1.0\nelement vertex {num_points}\n")
        f.write(
            "property float x\nproperty float y\nproperty float z\nproperty int cluster\nend_header\n"
        )

        # Save points in chunks to reduce memory usage
        for i in tqdm(range(0, num_points, chunk_size), desc="Saving chunks"):
            lines = (
                f"{pcd.points[j][0]} {pcd.points[j][1]} {pcd.points[j][2]} {labels[j]}\n"
                for j in range(i, min(i + chunk_size, num_points))
            )
            f.writelines(lines)

    logger.info(f"File saved: {output_path}")


def main(
    file_path: str,
    output_path: str,
    voxel_size: float = 0.1,
    min_cluster_size: int = 1000,
    min_samples: int = 100,
):
    """Main function to cluster and save the point cloud."""
    # Load and downsample the point cloud
    pcd = load_point_cloud(file_path)
    logger.info(f"Loaded point cloud with {len(pcd.points)} points")

    downsampled_pcd = downsample_point_cloud(pcd, voxel_size)
    logger.info(f"Downsampled point cloud to {len(downsampled_pcd.points)} points")

    # Apply HDBSCAN clustering
    downsampled_labels = apply_hdbscan(downsampled_pcd, min_cluster_size, min_samples)

    # Propagate the cluster labels to the original point cloud
    full_labels = propagate_labels_to_o3d(pcd, downsampled_pcd, downsampled_labels)

    # Save the clustered point cloud
    save_clustered_pcd_ply(pcd, full_labels, output_path)


if __name__ == "__main__":
    main("data/raw.ply", "data/clustered_output.ply")
