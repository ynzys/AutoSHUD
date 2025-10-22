"""
SHUD file I/O functions
All formats strictly follow SHUD C++ core program requirements
"""

from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple
import numpy as np
import pandas as pd


class SHUDFiles:
    """SHUD file naming convention"""

    def __init__(self, project_name: str, input_dir: Path, output_dir: Path):
        self.project_name = project_name
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

    def get_input_file(self, file_type: str) -> Path:
        """Get input file path"""
        extensions = {
            'mesh': f'{self.project_name}.sp.mesh',
            'riv': f'{self.project_name}.sp.riv',
            'att': f'{self.project_name}.sp.att',
            'rivseg': f'{self.project_name}.sp.rivseg',
            'soil': f'{self.project_name}.para.soil',
            'geol': f'{self.project_name}.para.geol',
            'lc': f'{self.project_name}.para.lc',
            'ic': f'{self.project_name}.cfg.ic',
            'para': f'{self.project_name}.cfg.para',
            'calib': f'{self.project_name}.cfg.calib',
            'forc': f'{self.project_name}.tsd.forc',
            'lai': f'{self.project_name}.tsd.lai',
            'rl': f'{self.project_name}.tsd.rl',
            'mf': f'{self.project_name}.tsd.mf',
        }
        return self.input_dir / extensions[file_type]


def write_mesh(mesh_data: pd.DataFrame, file_path: Union[str, Path]):
    """
    Write SHUD .sp.mesh file

    Format:
    Line 1: <ncells> <ncols>
    Line 2: ID Node1 Node2 Node3 Nabr1 Nabr2 Nabr3 Zmax
    Line 3+: data rows

    Args:
        mesh_data: DataFrame with columns [ID, Node1, Node2, Node3, Nabr1, Nabr2, Nabr3, Zmax]
        file_path: Output file path
    """
    ncells = len(mesh_data)
    ncols = 8  # Fixed: ID + 3 nodes + 3 neighbors + Zmax

    with open(file_path, 'w') as f:
        # Line 1: dimensions
        f.write(f"{ncells}\t{ncols}\n")

        # Line 2: column headers
        f.write("ID\tNode1\tNode2\tNode3\tNabr1\tNabr2\tNabr3\tZmax\n")

        # Line 3+: data (tab-separated)
        for _, row in mesh_data.iterrows():
            f.write(f"{row['ID']}\t{row['Node1']}\t{row['Node2']}\t{row['Node3']}\t"
                   f"{row['Nabr1']}\t{row['Nabr2']}\t{row['Nabr3']}\t{row['Zmax']:.2f}\n")


def write_river(river_data: pd.DataFrame, file_path: Union[str, Path]):
    """
    Write SHUD .sp.riv file

    Format similar to mesh file
    """
    nrivers = len(river_data)
    ncols = len(river_data.columns)

    with open(file_path, 'w') as f:
        f.write(f"{nrivers}\t{ncols}\n")

        # Write header
        header = '\t'.join(river_data.columns)
        f.write(f"{header}\n")

        # Write data
        for _, row in river_data.iterrows():
            line = '\t'.join([f"{val:.6f}" if isinstance(val, float) else str(val)
                            for val in row.values])
            f.write(f"{line}\n")


def write_attribute(att_data: pd.DataFrame, file_path: Union[str, Path]):
    """
    Write SHUD .sp.att file

    Format:
    Line 1: <ncells> <ncols>
    Line 2: INDEX SOIL GEOL LC FORC MF BC SS ilake
    Line 3+: data rows

    Args:
        att_data: DataFrame with columns [INDEX, SOIL, GEOL, LC, FORC, MF, BC, SS, ilake]
        file_path: Output file path
    """
    ncells = len(att_data)
    ncols = 9  # Fixed number of attribute columns

    with open(file_path, 'w') as f:
        f.write(f"{ncells}\t{ncols}\t\t\t\t\t\t\n")
        f.write("INDEX\tSOIL\tGEOL\tLC\tFORC\tMF\tBC\tSS\tilake\t\n")

        for _, row in att_data.iterrows():
            f.write(f"{row['INDEX']}\t{row['SOIL']}\t{row['GEOL']}\t{row['LC']}\t"
                   f"{row['FORC']}\t{row['MF']}\t{row['BC']}\t{row['SS']}\t{row['ilake']}\n")


def write_river_segment(rivseg_data: pd.DataFrame, file_path: Union[str, Path]):
    """Write SHUD .sp.rivseg file"""
    nsegs = len(rivseg_data)
    ncols = len(rivseg_data.columns)

    with open(file_path, 'w') as f:
        f.write(f"{nsegs}\t{ncols}\n")
        header = '\t'.join(rivseg_data.columns)
        f.write(f"{header}\n")

        for _, row in rivseg_data.iterrows():
            line = '\t'.join([f"{val:.6f}" if isinstance(val, float) else str(val)
                            for val in row.values])
            f.write(f"{line}\n")


def write_soil(soil_params: pd.DataFrame, file_path: Union[str, Path]):
    """
    Write SHUD .para.soil file

    Format:
    Line 1: <nsoil> <ncols>
    Line 2: INDEX KsatV(m_d) ThetaS(m3_m3) ThetaR(m3_m3) InfD(m) Alpha(1_m) Beta hAreaF(m2_m2) macKsatV(m_d)
    Line 3+: data rows

    Args:
        soil_params: DataFrame with soil parameters
        file_path: Output file path
    """
    nsoil = len(soil_params)
    ncols = len(soil_params.columns)

    with open(file_path, 'w') as f:
        f.write(f"{nsoil}\t{ncols}\n")

        # Column headers
        expected_cols = ['INDEX', 'KsatV(m_d)', 'ThetaS(m3_m3)', 'ThetaR(m3_m3)',
                        'InfD(m)', 'Alpha(1_m)', 'Beta', 'hAreaF(m2_m2)', 'macKsatV(m_d)']
        f.write('\t'.join(expected_cols) + '\n')

        for _, row in soil_params.iterrows():
            f.write(f"{row['INDEX']}\t{row['KsatV(m_d)']:.6f}\t{row['ThetaS(m3_m3)']:.6f}\t"
                   f"{row['ThetaR(m3_m3)']:.2f}\t{row['InfD(m)']:.1f}\t"
                   f"{row['Alpha(1_m)']:.6f}\t{row['Beta']:.6f}\t"
                   f"{row['hAreaF(m2_m2)']:.2f}\t{row['macKsatV(m_d)']:.2f}\n")


def write_geology(geol_params: pd.DataFrame, file_path: Union[str, Path]):
    """
    Write SHUD .para.geol file
    Similar format to soil file
    """
    ngeol = len(geol_params)
    ncols = len(geol_params.columns)

    with open(file_path, 'w') as f:
        f.write(f"{ngeol}\t{ncols}\n")

        # Write header
        header = '\t'.join(geol_params.columns)
        f.write(f"{header}\n")

        # Write data
        for _, row in geol_params.iterrows():
            line = '\t'.join([f"{val:.6f}" if isinstance(val, float) and 'INDEX' not in str(col)
                            else str(int(val)) if 'INDEX' in str(col) else f"{val}"
                            for col, val in zip(geol_params.columns, row.values)])
            f.write(f"{line}\n")


def write_landcover(lc_params: pd.DataFrame, file_path: Union[str, Path]):
    """Write SHUD .para.lc file"""
    nlc = len(lc_params)
    ncols = len(lc_params.columns)

    with open(file_path, 'w') as f:
        f.write(f"{nlc}\t{ncols}\n")
        header = '\t'.join(lc_params.columns)
        f.write(f"{header}\n")

        for _, row in lc_params.iterrows():
            line = '\t'.join([f"{val:.6f}" if isinstance(val, float) and 'INDEX' not in str(col)
                            else str(int(val)) if 'INDEX' in str(col) else f"{val}"
                            for col, val in zip(lc_params.columns, row.values)])
            f.write(f"{line}\n")


def write_initial_condition(ic_data: pd.DataFrame, file_path: Union[str, Path],
                           ncells: int, spinup_days: float = 5256000.0):
    """
    Write SHUD .cfg.ic file

    Format:
    Line 1: <ncells> <ncols> <spinup_days>
    Line 2: Index Canopy Snow Surface Unsat GW
    Line 3+: data rows

    Args:
        ic_data: DataFrame with columns [Index, Canopy, Snow, Surface, Unsat, GW]
        file_path: Output file path
        ncells: Number of cells
        spinup_days: Spinup period in days (in seconds: 5256000 = ~60.8 days)
    """
    ncols = 6  # Index + Canopy + Snow + Surface + Unsat + GW

    with open(file_path, 'w') as f:
        f.write(f"{ncells}\t {ncols} \t{spinup_days:.6f}\n")
        f.write("Index\tCanopy\tSnow\tSurface\tUnsat\tGW\n")

        for _, row in ic_data.iterrows():
            f.write(f"{int(row['Index'])}\t{row['Canopy']:.6f}\t{row['Snow']:.6f}\t"
                   f"{row['Surface']:.6f}\t{row['Unsat']:.6f}\t{row['GW']:.6f}\n")


def write_parameter(params: Dict[str, Union[int, float]], file_path: Union[str, Path]):
    """
    Write SHUD .cfg.para file

    Format: KEY<tab>VALUE

    Args:
        params: Dictionary of parameter name: value
        file_path: Output file path
    """
    with open(file_path, 'w') as f:
        for key, value in params.items():
            if isinstance(value, float):
                f.write(f"{key}\t{value:.6g}\n")
            else:
                f.write(f"{key}\t{value}\n")


def write_calibration(calib_params: Dict[str, Union[int, float]], file_path: Union[str, Path]):
    """
    Write SHUD .cfg.calib file

    Format: KEY<tab>VALUE (same as parameter file)
    Parameters with '+' suffix use addition, others use multiplication

    Args:
        calib_params: Dictionary of calibration parameter name: value
        file_path: Output file path
    """
    with open(file_path, 'w') as f:
        for key, value in calib_params.items():
            if isinstance(value, float):
                f.write(f"{key}\t{value:.6g}\n")
            else:
                f.write(f"{key}\t{value}\n")


def write_time_series(ts_data: pd.DataFrame, file_path: Union[str, Path],
                      file_type: str = 'forc'):
    """
    Write SHUD time series file (.tsd.*)

    Args:
        ts_data: Time series data (DataFrame or file reference)
        file_path: Output file path
        file_type: Type of time series ('forc', 'lai', 'rl', 'mf')
    """
    if file_type == 'forc':
        # For forcing, usually just write reference to CSV file
        with open(file_path, 'w') as f:
            f.write("CSV\t1\n")
            f.write("forcing.csv\n")
    else:
        # For LAI, RL, MF - write actual time series data
        with open(file_path, 'w') as f:
            # Write header: TS <ncols>
            ncols = len(ts_data.columns)
            f.write(f"TS\t{ncols}\n")

            # Write data
            for _, row in ts_data.iterrows():
                line = '\t'.join([f"{val:.6f}" if isinstance(val, float)
                                else str(val) for val in row.values])
                f.write(f"{line}\n")


def read_output(output_dir: Path, variable: str) -> np.ndarray:
    """
    Read SHUD output files

    Args:
        output_dir: Output directory path
        variable: Variable name (e.g., 'eleysurf', 'rivqdown')

    Returns:
        numpy array of output data
    """
    # SHUD outputs are in binary format
    # Implementation would depend on SHUD output format
    # Placeholder for now
    raise NotImplementedError("Output reading will be implemented based on SHUD output format")


def get_default_parameters(ndays: int) -> Dict[str, Union[int, float]]:
    """
    Get default SHUD model parameters

    Args:
        ndays: Number of simulation days

    Returns:
        Dictionary of default parameters
    """
    return {
        'VERBOSE': 0,
        'INIT_MODE': 3,
        'ASCII_OUTPUT': 0,
        'BINARY_OUTPUT': 1,
        'SPINUPDAY': 0,
        'NUM_OPENMP': 8,
        'SCR_INTV': 1440,
        'ABSTOL': 1e-4,
        'RELTOL': 1e-4,
        'INIT_SOLVER_STEP': 1,
        'MAX_SOLVER_STEP': 10,
        'LSM_STEP': 60,
        'START': 0,
        'END': ndays,
        'DT_YE_SNOW': 1440,
        'DT_YE_SURF': 1440,
        'DT_YE_UNSAT': 1440,
        'DT_YE_GW': 1440,
        'DT_QE_SURF': 1440,
        'DT_QE_SUB': 1440,
        'DT_QE_ET': 1440,
        'DT_QE_PRCP': 1440,
        'DT_QE_INFIL': 1440,
        'DT_QE_RECH': 1440,
        'DT_YR_STAGE': 1440,
        'DT_QR_DOWN': 1440,
        'DT_QR_SURF': 1440,
        'DT_QR_SUB': 1440,
        'DT_QR_UP': 1440,
    }


def get_default_calibration() -> Dict[str, Union[int, float]]:
    """
    Get default SHUD calibration parameters

    Returns:
        Dictionary of default calibration parameters
    """
    return {
        'GEOL_KSATH': 1.0,
        'GEOL_KSATV': 1.0,
        'GEOL_KMACSATH': 0.1,
        'GEOL_MACVF': 1.0,
        'GEOL_THETAS': 1.0,
        'GEOL_THETAR': 1.0,
        'GEOL_DMAC': 1.0,
        'SOIL_KINF': 0.01,
        'SOIL_KMACSATV': 1.0,
        'SOIL_DINF': 1.0,
        'SOIL_ALPHA': 1.0,
        'SOIL_BETA': 1.0,
        'SOIL_MACHF': 1.0,
        'LC_VEGFRAC': 1.0,
        'LC_ALBEDO': 1.0,
        'LC_ROUGH': 1.0,
        'LC_DROOT': 1.0,
        'LC_ISMAX': 1.0,
        'LC_IMPAF': 1.0,
        'LC_SOILDGD': 1.0,
        'TS_PRCP': 1.0,
        'TS_LAI': 1.0,
        'TS_SFCTMP+': 0.0,
        'ET_ETP': 1.0,
        'ET_IC': 1.0,
        'ET_TR': 1.0,
        'ET_SOIL': 1.0,
        'RIV_ROUGH': 1.0,
        'RIV_KH': 1.0,
        'RIV_SINU': 1.2,
        'RIV_CWR': 1.0,
        'RIV_BEDTHICK': 1.0,
        'RIV_BSLOPE+': 0.0,
        'RIV_DPTH+': 0.0,
        'RIV_WDTH+': 50.0,
        'IC_GW+': 0.0,
        'IC_RIV+': 0.0,
        'AQ_DEPTH+': 0.0,
    }
