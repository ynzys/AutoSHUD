"""
DEM (Digital Elevation Model) processing module
"""
from pathlib import Path
from typing import Optional
import geopandas as gpd
import rasterio
from loguru import logger

from ..config import ProjectConfig
from .spatial import SpatialUtils


class DEMProcessor:
    """DEM data processor"""

    def __init__(self, config: ProjectConfig):
        """
        Initialize DEM processor

        Args:
            config: Project configuration
        """
        self.config = config
        self.spatial_utils = SpatialUtils()

    def process(self):
        """Process DEM data - main entry point"""
        logger.info("Processing DEM and watershed boundary...")

        # Step 1: Load and process watershed boundary
        wbd_gcs, wbd_pcs = self._process_watershed_boundary()

        # Step 2: Create buffer
        buffer_pcs = self._create_buffer(wbd_pcs)

        # Step 3: Process DEM
        self._process_dem(buffer_pcs)

        # Step 4: Process stream network
        if self.config.stream_network:
            self._process_stream_network(wbd_pcs)

        # Step 5: Process lake (if exists)
        if self.config.lake:
            self._process_lake()

        logger.success("DEM processing completed")

    def _process_watershed_boundary(self):
        """Process watershed boundary"""
        logger.info("Loading watershed boundary...")

        # Read watershed boundary
        wbd = gpd.read_file(self.config.watershed_boundary)

        # Clean geometry
        wbd = wbd.buffer(0)  # Fix invalid geometries

        # Determine target CRS
        if self.config.crs_file and self.config.crs_file.exists():
            # Read CRS from file
            crs_gdf = gpd.read_file(self.config.crs_file)
            target_crs = crs_gdf.crs
        else:
            # Generate Albers projection
            target_crs = self.spatial_utils.get_albers_projection(wbd)

        # Reproject to PCS
        wbd_pcs = wbd.to_crs(target_crs)

        # Save GCS version
        wbd_gcs_path = self.config.predata_dir / 'gcs' / 'wbd.shp'
        wbd.to_file(wbd_gcs_path)

        # Save PCS version
        wbd_pcs_path = self.config.predata_dir / 'pcs' / 'wbd.shp'
        wbd_pcs.to_file(wbd_pcs_path)

        logger.info(f"Saved watershed boundary: GCS and PCS versions")
        return wbd, wbd_pcs

    def _create_buffer(self, wbd_pcs: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Create buffer around watershed"""
        buffer_distance = self.config.buffer_distance

        logger.info(f"Creating buffer: {buffer_distance}m")

        buffer_pcs = wbd_pcs.copy()
        buffer_pcs.geometry = wbd_pcs.buffer(buffer_distance)

        # Save PCS buffer
        buffer_pcs_path = self.config.predata_dir / 'pcs' / 'wbd_buf.shp'
        buffer_pcs.to_file(buffer_pcs_path)

        # Save GCS buffer
        buffer_gcs = buffer_pcs.to_crs('EPSG:4326')
        buffer_gcs_path = self.config.predata_dir / 'gcs' / 'wbd_buf.shp'
        buffer_gcs.to_file(buffer_gcs_path)

        logger.info("Buffer created and saved")
        return buffer_pcs

    def _process_dem(self, buffer_geom: gpd.GeoDataFrame):
        """Process DEM raster"""
        logger.info("Processing DEM...")

        if not self.config.dem or not self.config.dem.exists():
            logger.warning("DEM file not found, attempting to download...")
            self._download_dem()

        # Read DEM CRS
        with rasterio.open(self.config.dem) as src:
            dem_crs = src.crs

        # Clip DEM to buffer - GCS version
        dem_gcs_path = self.config.predata_dir / 'gcs' / 'dem.tif'
        self.spatial_utils.clip_raster(
            self.config.dem,
            dem_gcs_path,
            buffer_geom.to_crs(dem_crs)
        )

        # Reproject and clip to PCS
        dem_pcs_path = self.config.predata_dir / 'pcs' / 'dem.tif'
        self.spatial_utils.reproject_raster(
            dem_gcs_path,
            dem_pcs_path,
            buffer_geom.crs
        )

        logger.info(f"DEM processed: {dem_pcs_path}")

    def _process_stream_network(self, wbd_pcs: gpd.GeoDataFrame):
        """Process stream network"""
        logger.info("Processing stream network...")

        stream = gpd.read_file(self.config.stream_network)

        # Reproject to PCS
        stream_pcs = stream.to_crs(wbd_pcs.crs)

        # Simplify if needed
        if not self.config.quick_mode:
            # Calculate appropriate tolerance
            bounds = wbd_pcs.total_bounds
            tolerance = max((bounds[2] - bounds[0]), (bounds[3] - bounds[1])) / 1000
            stream_pcs = self.spatial_utils.simplify_geometry(stream_pcs, tolerance)

        # Save
        stream_pcs_path = self.config.predata_dir / 'pcs' / 'stm.shp'
        stream_pcs.to_file(stream_pcs_path)

        logger.info("Stream network processed")

    def _process_lake(self):
        """Process lake data"""
        logger.info("Processing lake data...")

        lake = gpd.read_file(self.config.lake)

        # Clean geometry
        lake = lake.buffer(0)

        # Save GCS version
        lake_gcs_path = self.config.predata_dir / 'gcs' / 'lake.shp'
        lake.to_file(lake_gcs_path)

        # Load wbd for CRS
        wbd_pcs = gpd.read_file(self.config.predata_dir / 'pcs' / 'wbd.shp')

        # Reproject to PCS
        lake_pcs = lake.to_crs(wbd_pcs.crs)
        lake_pcs_path = self.config.predata_dir / 'pcs' / 'lake.shp'
        lake_pcs.to_file(lake_pcs_path)

        logger.info("Lake data processed")

    def _download_dem(self):
        """Download DEM from ASTER GDEM (placeholder)"""
        logger.warning("DEM download not yet implemented")
        logger.info("Please provide DEM file manually")
        raise FileNotFoundError(f"DEM file not found: {self.config.dem}")
