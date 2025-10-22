"""
Result visualization module
"""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from loguru import logger

from ..config import ProjectConfig


class ResultVisualizer:
    """Result visualizer"""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.figure_dir = config.figure_dir
        self.figure_dir.mkdir(parents=True, exist_ok=True)

    def plot_all(self):
        """Plot all visualizations - main entry point"""
        logger.info("Generating visualizations...")

        self.plot_mesh()
        self.plot_watershed()
        # self.plot_timeseries()
        # self.plot_spatial_results()

        logger.success(f"Visualizations saved to: {self.figure_dir}")

    def plot_mesh(self):
        """Plot mesh"""
        logger.info("Plotting mesh...")

        try:
            # Load mesh
            mesh_file = self.config.model_input_dir / 'gis' / 'domain.shp'

            if not mesh_file.exists():
                logger.warning(f"Mesh file not found: {mesh_file}")
                return

            mesh = gpd.read_file(mesh_file)

            fig, ax = plt.subplots(figsize=(12, 10))
            mesh.plot(ax=ax, edgecolor='black', facecolor='lightblue', linewidth=0.5)
            ax.set_title('SHUD Mesh')
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')

            output_file = self.figure_dir / 'mesh.png'
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Mesh plot saved: {output_file}")

        except Exception as e:
            logger.error(f"Failed to plot mesh: {e}")

    def plot_watershed(self):
        """Plot watershed boundary"""
        logger.info("Plotting watershed...")

        try:
            wbd_file = self.config.predata_dir / 'pcs' / 'wbd.shp'

            if not wbd_file.exists():
                logger.warning(f"Watershed file not found: {wbd_file}")
                return

            wbd = gpd.read_file(wbd_file)

            # Try to load DEM
            dem_file = self.config.predata_dir / 'pcs' / 'dem.tif'

            fig, ax = plt.subplots(figsize=(12, 10))

            if dem_file.exists():
                import rasterio
                from rasterio.plot import show

                with rasterio.open(dem_file) as src:
                    show(src, ax=ax, cmap='terrain', alpha=0.7)

            wbd.plot(ax=ax, edgecolor='red', facecolor='none', linewidth=2)

            # Try to plot stream network
            stm_file = self.config.predata_dir / 'pcs' / 'stm.shp'
            if stm_file.exists():
                stm = gpd.read_file(stm_file)
                stm.plot(ax=ax, color='blue', linewidth=1)

            ax.set_title('Watershed')
            ax.set_xlabel('X (m)')
            ax.set_ylabel('Y (m)')

            output_file = self.figure_dir / 'watershed.png'
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()

            logger.info(f"Watershed plot saved: {output_file}")

        except Exception as e:
            logger.error(f"Failed to plot watershed: {e}")

    def plot_timeseries(self, data: pd.DataFrame, title: str, ylabel: str, output_name: str):
        """Plot time series"""
        fig, ax = plt.subplots(figsize=(12, 6))

        for col in data.columns:
            if col != 'Date' and col != 'date':
                ax.plot(data['Date'], data[col], label=col)

        ax.set_title(title)
        ax.set_xlabel('Date')
        ax.set_ylabel(ylabel)
        ax.legend()
        ax.grid(True, alpha=0.3)

        output_file = self.figure_dir / f'{output_name}.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Time series plot saved: {output_file}")

    def plot_spatial_results(self, variable: str, data: gpd.GeoDataFrame):
        """Plot spatial results"""
        fig, ax = plt.subplots(figsize=(12, 10))

        data.plot(
            column=variable,
            ax=ax,
            legend=True,
            cmap='viridis',
            edgecolor='black',
            linewidth=0.2
        )

        ax.set_title(f'{variable} Distribution')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')

        output_file = self.figure_dir / f'{variable}_spatial.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()

        logger.info(f"Spatial plot saved: {output_file}")
