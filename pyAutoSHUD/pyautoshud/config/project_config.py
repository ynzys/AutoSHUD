"""
Project configuration module - handles YAML configuration files
"""
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
    """Project configuration class - equivalent to ReadProject.R"""

    # Project basic info
    name: str
    start_year: int
    end_year: int
    output_dir: Path

    # Input data paths
    dem: Optional[Path] = None
    watershed_boundary: Optional[Path] = None
    stream_network: Optional[Path] = None
    lake: Optional[Path] = None
    crs_file: Optional[Path] = None

    # Data source configuration
    soil_source: str = "isric"  # isric, ssurgo, or local
    soil_data_dir: Optional[Path] = None
    soil_file: Optional[Path] = None
    soil_table: Optional[Path] = None

    landcover_source: str = "glc"  # glc, nlcd, or local
    landcover_file: Optional[Path] = None
    landcover_table: Optional[Path] = None

    forcing_source: str = "gldas"  # gldas, nldas, cmfd, cmip6, or local
    forcing_data_dir: Optional[Path] = None
    forcing_file: Optional[Path] = None
    forcing_output_dir: Optional[Path] = None

    # Model parameters
    num_cells: int = 1000
    max_area_km2: float = 10.0
    min_angle: float = 31.0
    aquifer_depth: float = 20.0
    buffer_distance: float = 5000.0
    quick_mode: bool = False
    flowpath: bool = False

    # River parameters
    river_width: Optional[float] = None
    river_depth: Optional[float] = None
    tol_watershed_boundary: Optional[float] = None
    tol_river_length: Optional[float] = None

    # Simulation parameters
    start_day: int = 0
    end_day: Optional[int] = None
    max_solver_step: int = 2
    cryosphere: bool = False

    # Derived paths
    predata_dir: Optional[Path] = None
    model_input_dir: Optional[Path] = None
    model_output_dir: Optional[Path] = None
    figure_dir: Optional[Path] = None

    @classmethod
    def from_yaml(cls, yaml_file: str) -> 'ProjectConfig':
        """
        Load configuration from YAML file

        Args:
            yaml_file: Path to YAML configuration file

        Returns:
            ProjectConfig instance
        """
        with open(yaml_file, 'r') as f:
            config = yaml.safe_load(f)

        return cls.from_dict(config)

    @classmethod
    def from_txt(cls, txt_file: str) -> 'ProjectConfig':
        """
        Load configuration from R-style text file (backward compatibility)

        Args:
            txt_file: Path to text configuration file (R format)

        Returns:
            ProjectConfig instance
        """
        config = {}
        with open(txt_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # Parse "key" "value" format
                parts = line.split(None, 1)
                if len(parts) == 2:
                    key = parts[0].strip('"')
                    value = parts[1].strip('"')
                    config[key] = value

        # Map R config keys to Python config
        return cls._from_r_config(config)

    @classmethod
    def _from_r_config(cls, r_config: Dict[str, str]) -> 'ProjectConfig':
        """Convert R-style config to Python config"""

        def get_val(key: str, default=None, convert=str):
            val = r_config.get(key, default)
            if val is None:
                return default
            try:
                return convert(val)
            except:
                return default

        # Calculate end_day if not provided
        start_year = get_val('startyear', convert=int)
        end_year = get_val('endyear', convert=int)
        years = list(range(start_year, end_year + 1))
        end_day = get_val('ENDDAY', convert=int)
        if end_day is None:
            # Calculate total days
            ndays = sum(366 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                       else 365 for y in years)
            end_day = ndays

        output_dir = Path(get_val('dir.out', './output'))
        prjname = get_val('prjname', 'project')

        return cls(
            name=prjname,
            start_year=start_year,
            end_year=end_year,
            output_dir=output_dir,
            dem=Path(get_val('fr.dem')) if get_val('fr.dem') else None,
            watershed_boundary=Path(get_val('fsp.wbd')) if get_val('fsp.wbd') else None,
            stream_network=Path(get_val('fsp.stm')) if get_val('fsp.stm') else None,
            lake=Path(get_val('fsp.lake')) if get_val('fsp.lake') else None,
            crs_file=Path(get_val('fsp.crs')) if get_val('fsp.crs') else None,

            soil_source="local" if get_val('Soil', '0', int) >= 1 else "isric",
            soil_data_dir=Path(get_val('dir.soil')) if get_val('dir.soil') else None,
            soil_file=Path(get_val('fn.soil')) if get_val('fn.soil') else None,
            soil_table=Path(get_val('tab.soil')) if get_val('tab.soil') else None,

            landcover_source="local" if get_val('landuse', '0', int) >= 1 else "glc",
            landcover_file=Path(get_val('fn.landuse')) if get_val('fn.landuse') else None,
            landcover_table=Path(get_val('tab.landuse')) if get_val('tab.landuse') else None,

            forcing_source="local" if get_val('forcing', '0', int) >= 1 else "gldas",
            forcing_data_dir=Path(get_val('dir.ldas')) if get_val('dir.ldas') else None,
            forcing_output_dir=Path(get_val('dout.forc')) if get_val('dout.forc') else None,

            num_cells=get_val('NumCells', 1000, int),
            max_area_km2=get_val('MaxArea_km2', 10.0, float),
            min_angle=get_val('MinAngle', 31.0, float),
            aquifer_depth=get_val('AqDepth', 20.0, float),
            buffer_distance=get_val('DistBuffer', 5000.0, float),
            quick_mode=get_val('QuickMode', '0', int) > 0,
            flowpath=get_val('flowpath', '0', int) > 0,

            river_width=get_val('RivWidth', convert=float),
            river_depth=get_val('RivDepth', convert=float),
            tol_watershed_boundary=get_val('tol.wb', convert=float),
            tol_river_length=get_val('tol.rivlen', convert=float),

            start_day=get_val('STARTDAY', 0, int),
            end_day=end_day,
            max_solver_step=get_val('MAX_SOLVER_STEP', 2, int),
            cryosphere=get_val('CRYOSPHERE', '0', int) > 0,

            predata_dir=output_dir / 'DataPre',
            model_input_dir=output_dir / 'input' / prjname,
            model_output_dir=output_dir / 'output' / f'{prjname}.out',
            figure_dir=output_dir / 'Image',
        )

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ProjectConfig':
        """Create config from dictionary (from YAML)"""
        proj = config_dict.get('project', {})
        data = config_dict.get('data', {})
        model = config_dict.get('model', {})
        sim = config_dict.get('simulation', {})

        output_dir = Path(proj.get('output_dir', './output'))
        prjname = proj.get('name', 'project')

        return cls(
            name=prjname,
            start_year=proj['start_year'],
            end_year=proj['end_year'],
            output_dir=output_dir,

            dem=Path(data.get('dem')) if data.get('dem') else None,
            watershed_boundary=Path(data.get('watershed_boundary')) if data.get('watershed_boundary') else None,
            stream_network=Path(data.get('stream_network')) if data.get('stream_network') else None,
            lake=Path(data.get('lake')) if data.get('lake') else None,

            soil_source=data.get('soil', {}).get('source', 'isric'),
            soil_data_dir=Path(data.get('soil', {}).get('data_dir')) if data.get('soil', {}).get('data_dir') else None,

            landcover_source=data.get('landcover', {}).get('source', 'glc'),
            landcover_file=Path(data.get('landcover', {}).get('file')) if data.get('landcover', {}).get('file') else None,

            forcing_source=data.get('forcing', {}).get('source', 'gldas'),
            forcing_data_dir=Path(data.get('forcing', {}).get('data_dir')) if data.get('forcing', {}).get('data_dir') else None,

            num_cells=model.get('num_cells', 1000),
            max_area_km2=model.get('max_area_km2', 10.0),
            min_angle=model.get('min_angle', 31.0),
            aquifer_depth=model.get('aquifer_depth', 20.0),
            buffer_distance=model.get('buffer_distance', 5000.0),

            start_day=sim.get('start_day', 0),
            end_day=sim.get('end_day'),
            max_solver_step=sim.get('solver_step', 2),
            cryosphere=sim.get('cryosphere', False),

            predata_dir=output_dir / 'DataPre',
            model_input_dir=output_dir / 'input' / prjname,
            model_output_dir=output_dir / 'output' / f'{prjname}.out',
            figure_dir=output_dir / 'Image',
        )

    def create_directories(self):
        """Create all output directories"""
        for dir_path in [self.output_dir, self.predata_dir, self.model_input_dir,
                         self.model_output_dir, self.figure_dir]:
            if dir_path:
                dir_path.mkdir(parents=True, exist_ok=True)

        # Create GCS and PCS subdirectories
        (self.predata_dir / 'gcs').mkdir(parents=True, exist_ok=True)
        (self.predata_dir / 'pcs').mkdir(parents=True, exist_ok=True)

        # Create GIS subdirectory in model input
        (self.model_input_dir / 'gis').mkdir(parents=True, exist_ok=True)

    def to_yaml(self, yaml_file: str):
        """Save configuration to YAML file"""
        config = {
            'project': {
                'name': self.name,
                'start_year': self.start_year,
                'end_year': self.end_year,
                'output_dir': str(self.output_dir),
            },
            'data': {
                'dem': str(self.dem) if self.dem else None,
                'watershed_boundary': str(self.watershed_boundary) if self.watershed_boundary else None,
                'stream_network': str(self.stream_network) if self.stream_network else None,
                'lake': str(self.lake) if self.lake else None,
                'soil': {
                    'source': self.soil_source,
                    'data_dir': str(self.soil_data_dir) if self.soil_data_dir else None,
                },
                'landcover': {
                    'source': self.landcover_source,
                    'file': str(self.landcover_file) if self.landcover_file else None,
                },
                'forcing': {
                    'source': self.forcing_source,
                    'data_dir': str(self.forcing_data_dir) if self.forcing_data_dir else None,
                },
            },
            'model': {
                'num_cells': self.num_cells,
                'max_area_km2': self.max_area_km2,
                'min_angle': self.min_angle,
                'aquifer_depth': self.aquifer_depth,
                'buffer_distance': self.buffer_distance,
            },
            'simulation': {
                'start_day': self.start_day,
                'end_day': self.end_day,
                'solver_step': self.max_solver_step,
                'cryosphere': self.cryosphere,
            },
        }

        with open(yaml_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
