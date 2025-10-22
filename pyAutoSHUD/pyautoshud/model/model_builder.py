"""
SHUD model builder - generates all input files
"""
from pathlib import Path
import pandas as pd
import numpy as np
from loguru import logger

from ..config import ProjectConfig
from ..io import (
    write_mesh, write_attribute, write_soil, write_geology,
    write_landcover, write_initial_condition, write_parameter,
    write_calibration, write_time_series,
    get_default_parameters, get_default_calibration, SHUDFiles
)


class SHUDModelBuilder:
    """SHUD model builder"""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.files = SHUDFiles(
            config.name,
            config.model_input_dir,
            config.model_output_dir
        )

    def build(self, mesh_data: dict):
        """
        Build SHUD model - main entry point

        Args:
            mesh_data: Mesh data from MeshGenerator
        """
        logger.info("Building SHUD model...")

        mesh_df = mesh_data['mesh']
        ncells = len(mesh_df)

        # 1. Write mesh file
        self._write_mesh_file(mesh_df)

        # 2. Generate and write attribute file
        self._write_attribute_file(ncells)

        # 3. Generate and write parameter files
        self._write_parameter_files(ncells)

        # 4. Generate initial conditions
        self._write_initial_conditions(ncells)

        # 5. Generate model parameters
        self._write_model_parameters()

        # 6. Generate calibration parameters
        self._write_calibration_parameters()

        # 7. Generate time series data
        self._write_time_series()

        logger.success(f"SHUD model built: {ncells} cells")

    def _write_mesh_file(self, mesh_df: pd.DataFrame):
        """Write mesh file"""
        output_file = self.files.get_input_file('mesh')
        write_mesh(mesh_df, output_file)
        logger.info(f"Mesh file written: {output_file.name}")

    def _write_attribute_file(self, ncells: int):
        """Write attribute file"""
        # Create default attributes
        att_df = pd.DataFrame({
            'INDEX': range(1, ncells + 1),
            'SOIL': 1,
            'GEOL': 1,
            'LC': 11,  # Default land cover type
            'FORC': 1,
            'MF': 1,
            'BC': 0,
            'SS': 0,
            'ilake': 0
        })

        output_file = self.files.get_input_file('att')
        write_attribute(att_df, output_file)
        logger.info(f"Attribute file written: {output_file.name}")

    def _write_parameter_files(self, ncells: int):
        """Write soil, geology, and land cover parameter files"""

        # Soil parameters
        soil_params = pd.DataFrame({
            'INDEX': [1],
            'KsatV(m_d)': [0.25],
            'ThetaS(m3_m3)': [0.40],
            'ThetaR(m3_m3)': [0.01],
            'InfD(m)': [0.1],
            'Alpha(1_m)': [3.5],
            'Beta': [1.2],
            'hAreaF(m2_m2)': [0.01],
            'macKsatV(m_d)': [25.0]
        })

        output_file = self.files.get_input_file('soil')
        write_soil(soil_params, output_file)
        logger.info(f"Soil parameters written: {output_file.name}")

        # Geology parameters (same as soil for now)
        geol_params = soil_params.copy()
        output_file = self.files.get_input_file('geol')
        write_geology(geol_params, output_file)
        logger.info(f"Geology parameters written: {output_file.name}")

        # Land cover parameters
        lc_params = pd.DataFrame({
            'INDEX': [11],
            'VegFrac': [0.50],
            'Albedo': [0.18],
            'Rough': [0.10],
            'RzD': [1.0],
            'LAImax': [4.0],
        })

        output_file = self.files.get_input_file('lc')
        write_landcover(lc_params, output_file)
        logger.info(f"Land cover parameters written: {output_file.name}")

    def _write_initial_conditions(self, ncells: int):
        """Write initial conditions file"""
        ic_df = pd.DataFrame({
            'Index': range(1, ncells + 1),
            'Canopy': 0.0,
            'Snow': 0.0,
            'Surface': 0.0,
            'Unsat': self.config.aquifer_depth * 0.5,  # 50% saturation
            'GW': 0.02  # 2cm groundwater depth
        })

        output_file = self.files.get_input_file('ic')
        write_initial_condition(ic_df, output_file, ncells)
        logger.info(f"Initial conditions written: {output_file.name}")

    def _write_model_parameters(self):
        """Write model parameter file"""
        # Calculate simulation days
        years = list(range(self.config.start_year, self.config.end_year + 1))
        ndays = sum(366 if y % 4 == 0 else 365 for y in years)

        if self.config.end_day:
            ndays = self.config.end_day

        params = get_default_parameters(ndays)

        # Update with config values
        params['START'] = self.config.start_day
        params['END'] = self.config.end_day or ndays
        params['MAX_SOLVER_STEP'] = self.config.max_solver_step
        params['CRYOSPHERE'] = 1 if self.config.cryosphere else 0

        output_file = self.files.get_input_file('para')
        write_parameter(params, output_file)
        logger.info(f"Model parameters written: {output_file.name}")

    def _write_calibration_parameters(self):
        """Write calibration parameter file"""
        calib_params = get_default_calibration()

        output_file = self.files.get_input_file('calib')
        write_calibration(calib_params, output_file)
        logger.info(f"Calibration parameters written: {output_file.name}")

    def _write_time_series(self):
        """Write time series files"""
        # Forcing data reference
        forc_file = self.files.get_input_file('forc')
        write_time_series(pd.DataFrame(), forc_file, file_type='forc')

        # LAI time series (simplified - constant value)
        years = list(range(self.config.start_year, self.config.end_year + 1))
        ndays = sum(366 if y % 4 == 0 else 365 for y in years)

        lai_data = pd.DataFrame({
            'Day': range(1, ndays + 1),
            'LAI': 3.0  # Constant LAI
        })

        lai_file = self.files.get_input_file('lai')
        write_time_series(lai_data, lai_file, file_type='lai')

        # Roughness length (simplified)
        rl_data = pd.DataFrame({
            'Day': range(1, ndays + 1),
            'RL': 0.1  # Constant roughness
        })

        rl_file = self.files.get_input_file('rl')
        write_time_series(rl_data, rl_file, file_type='rl')

        # Melt factor (simplified)
        mf_data = pd.DataFrame({
            'Day': range(1, ndays + 1),
            'MF': 3.0  # Constant melt factor
        })

        mf_file = self.files.get_input_file('mf')
        write_time_series(mf_data, mf_file, file_type='mf')

        logger.info("Time series files written")
