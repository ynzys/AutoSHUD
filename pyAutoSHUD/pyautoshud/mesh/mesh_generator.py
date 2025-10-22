"""
Mesh generation using Delaunay triangulation
"""
from pathlib import Path
from typing import Tuple, Optional
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, Polygon
import triangle as tr
from loguru import logger

from ..config import ProjectConfig


class MeshGenerator:
    """Mesh generator using triangle library"""

    def __init__(self, config: ProjectConfig):
        self.config = config

    def generate(self) -> dict:
        """
        Generate mesh - main entry point

        Returns:
            dict with mesh data
        """
        logger.info("Generating mesh...")

        # Load watershed boundary
        wbd = gpd.read_file(self.config.predata_dir / 'pcs' / 'wbd.shp')

        # Simplify boundary
        wbd_simplified = self._simplify_boundary(wbd)

        # Generate mesh
        mesh_data = self._generate_delaunay_mesh(wbd_simplified)

        # Extract mesh properties
        mesh_df = self._create_mesh_dataframe(mesh_data, wbd)

        logger.success(f"Mesh generated: {len(mesh_df)} cells")
        return {'mesh': mesh_df, 'raw': mesh_data}

    def _simplify_boundary(self, wbd: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Simplify watershed boundary"""
        # Calculate tolerance based on target area
        area = wbd.geometry.area.sum()
        target_area = self.config.max_area_km2 * 1e6  # Convert to m²
        tolerance = min(np.sqrt(target_area), 3000)

        logger.info(f"Simplifying boundary with tolerance={tolerance:.0f}m")

        wbd_simp = wbd.copy()
        wbd_simp.geometry = wbd.simplify(tolerance, preserve_topology=True)

        return wbd_simp

    def _generate_delaunay_mesh(self, wbd: gpd.GeoDataFrame) -> dict:
        """Generate Delaunay triangulation"""
        logger.info("Creating Delaunay triangulation...")

        # Extract boundary coordinates
        boundary = wbd.geometry.iloc[0]
        if boundary.geom_type == 'MultiPolygon':
            boundary = max(boundary.geoms, key=lambda x: x.area)

        coords = np.array(boundary.exterior.coords[:-1])  # Remove duplicate last point

        # Calculate target area
        total_area = wbd.geometry.area.sum()
        target_cells = self.config.num_cells
        max_area = min(total_area / target_cells, self.config.max_area_km2 * 1e6)

        # Create triangle input
        segments = np.array([[i, (i+1) % len(coords)] for i in range(len(coords))])

        tri_input = {
            'vertices': coords,
            'segments': segments,
        }

        # Triangle options:
        # p - PSLG, q - quality (min angle), a - max area
        min_angle = self.config.min_angle
        opts = f'pq{min_angle}a{max_area:.0f}'

        logger.info(f"Triangle options: {opts}")

        try:
            mesh = tr.triangulate(tri_input, opts)
            logger.info(f"Generated {len(mesh['triangles'])} triangles")
            return mesh
        except Exception as e:
            logger.error(f"Mesh generation failed: {e}")
            # Fallback to simpler mesh
            logger.warning("Falling back to simpler mesh without area constraint")
            mesh = tr.triangulate(tri_input, f'pq{min_angle}')
            return mesh

    def _create_mesh_dataframe(self, mesh_data: dict, wbd: gpd.GeoDataFrame) -> pd.DataFrame:
        """Create mesh DataFrame in SHUD format"""
        vertices = mesh_data['vertices']
        triangles = mesh_data['triangles']

        mesh_list = []

        for i, tri in enumerate(triangles):
            # Get vertices
            v1, v2, v3 = tri

            # Find neighbors (triangles sharing edges)
            neighbors = self._find_neighbors(i, triangles)

            # Calculate max elevation (placeholder - would extract from DEM)
            tri_coords = vertices[[v1, v2, v3]]
            zmax = 1000.0  # Default elevation

            mesh_list.append({
                'ID': i + 1,
                'Node1': v1 + 1,  # 1-indexed
                'Node2': v2 + 1,
                'Node3': v3 + 1,
                'Nabr1': neighbors[0],
                'Nabr2': neighbors[1],
                'Nabr3': neighbors[2],
                'Zmax': zmax
            })

        return pd.DataFrame(mesh_list)

    def _find_neighbors(self, tri_idx: int, triangles: np.ndarray) -> list:
        """Find neighboring triangles"""
        tri = set(triangles[tri_idx])
        neighbors = [0, 0, 0]

        for j, other_tri in enumerate(triangles):
            if j == tri_idx:
                continue

            other = set(other_tri)
            shared = tri & other

            if len(shared) == 2:  # Shared edge
                # Determine which neighbor position
                for k in range(3):
                    if neighbors[k] == 0:
                        neighbors[k] = j + 1  # 1-indexed
                        break

        return neighbors
