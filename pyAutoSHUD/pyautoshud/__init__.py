"""
pyAutoSHUD - Python-based Automated Hydrological Model Deployment Tool

A Python rewrite of the R-based AutoSHUD for SHUD hydrological model deployment.
"""

__version__ = "1.0.0"
__author__ = "AutoSHUD Contributors"

from .config import ProjectConfig
from .data import DEMProcessor, SoilProcessor, LandcoverProcessor, ForcingProcessor
from .mesh import MeshGenerator
from .model import SHUDModelBuilder
from .runner import SHUDRunner
from .analysis import WaterBalanceAnalyzer, ResultVisualizer
from .calibration import ModelCalibrator

__all__ = [
    "ProjectConfig",
    "DEMProcessor",
    "SoilProcessor",
    "LandcoverProcessor",
    "ForcingProcessor",
    "MeshGenerator",
    "SHUDModelBuilder",
    "SHUDRunner",
    "WaterBalanceAnalyzer",
    "ResultVisualizer",
    "ModelCalibrator",
]
