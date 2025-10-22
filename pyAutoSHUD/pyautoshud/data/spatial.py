"""
Spatial utility functions for geospatial data processing
"""
from pathlib import Path
from typing import Union, Tuple, Optional
import geopandas as gpd
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
from rasterio.mask import mask
from shapely.geometry import box
import numpy as np
from loguru import logger


class SpatialUtils:
    """Spatial data processing utilities"""

    @staticmethod
    def reproject_raster(
        src_path: Union[str, Path],
        dst_path: Union[str, Path],
        dst_crs: str,
        src_crs: Optional[str] = None,
        resampling: str = 'bilinear'
    ):
        """
        Reproject raster to different CRS

        Args:
            src_path: Source raster path
            dst_path: Destination raster path
            dst_crs: Target CRS
            src_crs: Source CRS (if None, use raster's CRS)
            resampling: Resampling method
        """
        resampling_methods = {
            'nearest': Resampling.nearest,
            'bilinear': Resampling.bilinear,
            'cubic': Resampling.cubic,
            'average': Resampling.average,
        }

        with rasterio.open(src_path) as src:
            src_crs = src_crs or src.crs

            transform, width, height = calculate_default_transform(
                src_crs, dst_crs, src.width, src.height, *src.bounds
            )

            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with rasterio.open(dst_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src_crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=resampling_methods.get(resampling, Resampling.bilinear)
                    )

        logger.info(f"Reprojected raster: {src_path} -> {dst_path}")

    @staticmethod
    def clip_raster(
        raster_path: Union[str, Path],
        output_path: Union[str, Path],
        geometry: gpd.GeoDataFrame,
        crop: bool = True
    ):
        """
        Clip raster by geometry

        Args:
            raster_path: Input raster path
            output_path: Output raster path
            geometry: Clipping geometry (GeoDataFrame)
            crop: Crop to geometry extent
        """
        with rasterio.open(raster_path) as src:
            out_image, out_transform = mask(
                src, geometry.geometry, crop=crop, all_touched=True
            )

            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform
            })

            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(out_image)

        logger.info(f"Clipped raster: {raster_path} -> {output_path}")

    @staticmethod
    def create_buffer(
        geometry: gpd.GeoDataFrame,
        distance: float,
        output_path: Optional[Union[str, Path]] = None
    ) -> gpd.GeoDataFrame:
        """
        Create buffer around geometry

        Args:
            geometry: Input geometry
            distance: Buffer distance in CRS units
            output_path: Optional output path

        Returns:
            Buffered geometry
        """
        # Ensure projected CRS for accurate buffering
        if geometry.crs.is_geographic:
            logger.warning("Input CRS is geographic, buffer distance may be inaccurate")

        buffered = geometry.copy()
        buffered.geometry = geometry.buffer(distance)

        if output_path:
            buffered.to_file(output_path)
            logger.info(f"Saved buffered geometry to {output_path}")

        return buffered

    @staticmethod
    def reproject_vector(
        gdf: gpd.GeoDataFrame,
        target_crs: str,
        output_path: Optional[Union[str, Path]] = None
    ) -> gpd.GeoDataFrame:
        """
        Reproject vector data

        Args:
            gdf: Input GeoDataFrame
            target_crs: Target CRS
            output_path: Optional output path

        Returns:
            Reprojected GeoDataFrame
        """
        reprojected = gdf.to_crs(target_crs)

        if output_path:
            reprojected.to_file(output_path)
            logger.info(f"Saved reprojected vector to {output_path}")

        return reprojected

    @staticmethod
    def extract_raster_values(
        raster_path: Union[str, Path],
        geometries: gpd.GeoDataFrame,
        stats: list = ['mean', 'min', 'max']
    ) -> gpd.GeoDataFrame:
        """
        Extract raster values for geometries (zonal statistics)

        Args:
            raster_path: Raster file path
            geometries: Geometries to extract values for
            stats: Statistics to compute

        Returns:
            GeoDataFrame with extracted values
        """
        import rasterstats

        result = geometries.copy()

        for stat in stats:
            values = rasterstats.zonal_stats(
                geometries.geometry,
                str(raster_path),
                stats=stat
            )
            result[f'raster_{stat}'] = [v[stat] for v in values]

        logger.info(f"Extracted raster values: {stats}")
        return result

    @staticmethod
    def get_albers_projection(geometry: gpd.GeoDataFrame) -> str:
        """
        Get Albers Equal Area projection for geometry

        Args:
            geometry: Input geometry

        Returns:
            Albers projection string
        """
        bounds = geometry.total_bounds  # minx, miny, maxx, maxy
        lon_0 = (bounds[0] + bounds[2]) / 2
        lat_0 = (bounds[1] + bounds[3]) / 2
        lat_1 = bounds[1] + (bounds[3] - bounds[1]) * 0.25
        lat_2 = bounds[1] + (bounds[3] - bounds[1]) * 0.75

        albers = (
            f"+proj=aea +lat_1={lat_1:.6f} +lat_2={lat_2:.6f} "
            f"+lat_0={lat_0:.6f} +lon_0={lon_0:.6f} "
            f"+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
        )

        logger.info(f"Generated Albers projection: center=({lon_0:.4f}, {lat_0:.4f})")
        return albers

    @staticmethod
    def simplify_geometry(
        geometry: gpd.GeoDataFrame,
        tolerance: float,
        preserve_topology: bool = True
    ) -> gpd.GeoDataFrame:
        """
        Simplify geometry

        Args:
            geometry: Input geometry
            tolerance: Simplification tolerance
            preserve_topology: Preserve topology

        Returns:
            Simplified geometry
        """
        simplified = geometry.copy()
        simplified.geometry = geometry.simplify(
            tolerance, preserve_topology=preserve_topology
        )

        logger.info(f"Simplified geometry with tolerance={tolerance}")
        return simplified
