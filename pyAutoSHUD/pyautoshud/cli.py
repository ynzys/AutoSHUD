"""
Command-line interface for pyAutoSHUD
"""
import click
from pathlib import Path
import sys
from loguru import logger

from .config import ProjectConfig
from .workflow import AutoSHUDWorkflow


@click.group()
@click.version_option(version='1.0.0')
def main():
    """pyAutoSHUD - Python-based Automated Hydrological Model Deployment Tool"""
    logger.remove()
    logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--step', '-s', multiple=True, help='Specific step(s) to run')
@click.option('--skip-preprocessing', is_flag=True, help='Skip data preprocessing')
@click.option('--skip-model-build', is_flag=True, help='Skip model building')
@click.option('--skip-simulation', is_flag=True, help='Skip model simulation')
def run(config_file, step, skip_preprocessing, skip_model_build, skip_simulation):
    """Run complete pyAutoSHUD workflow"""

    logger.info(f"Loading configuration from {config_file}")

    # Load configuration
    if config_file.endswith('.yaml') or config_file.endswith('.yml'):
        config = ProjectConfig.from_yaml(config_file)
    else:
        config = ProjectConfig.from_txt(config_file)

    logger.info(f"Project: {config.name}")
    logger.info(f"Simulation period: {config.start_year}-{config.end_year}")

    # Create workflow
    workflow = AutoSHUDWorkflow(config)

    # Run workflow
    if not step:
        workflow.run_all(
            skip_preprocessing=skip_preprocessing,
            skip_model_build=skip_model_build,
            skip_simulation=skip_simulation
        )
    else:
        for s in step:
            workflow.run_step(s)


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
def preprocess(config_file):
    """Run data preprocessing only"""
    config = ProjectConfig.from_yaml(config_file) if config_file.endswith('.yaml') else ProjectConfig.from_txt(config_file)
    workflow = AutoSHUDWorkflow(config)
    workflow.preprocess_data()


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
def build(config_file):
    """Build SHUD model"""
    config = ProjectConfig.from_yaml(config_file) if config_file.endswith('.yaml') else ProjectConfig.from_txt(config_file)
    workflow = AutoSHUDWorkflow(config)
    workflow.build_model()


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--compile-only', is_flag=True, help='Compile SHUD only, do not run')
def simulate(config_file, compile_only):
    """Run SHUD simulation"""
    config = ProjectConfig.from_yaml(config_file) if config_file.endswith('.yaml') else ProjectConfig.from_txt(config_file)
    workflow = AutoSHUDWorkflow(config)

    if compile_only:
        workflow.compile_shud()
    else:
        workflow.run_simulation()


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--algorithm', '-a', default='NSGA2', help='Calibration algorithm (NSGA2, PSO, SCE-UA, DDS)')
@click.option('--iterations', '-i', default=100, help='Number of iterations')
@click.option('--output', '-o', default='calibration_results.csv', help='Output file')
def calibrate(config_file, algorithm, iterations, output):
    """Run model calibration"""
    config = ProjectConfig.from_yaml(config_file) if config_file.endswith('.yaml') else ProjectConfig.from_txt(config_file)
    workflow = AutoSHUDWorkflow(config)

    logger.info(f"Starting calibration with {algorithm} algorithm")
    workflow.calibrate(algorithm=algorithm, iterations=iterations, output_file=output)


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
def analyze(config_file):
    """Analyze simulation results"""
    config = ProjectConfig.from_yaml(config_file) if config_file.endswith('.yaml') else ProjectConfig.from_txt(config_file)
    workflow = AutoSHUDWorkflow(config)
    workflow.analyze_results()


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
def visualize(config_file):
    """Visualize simulation results"""
    config = ProjectConfig.from_yaml(config_file) if config_file.endswith('.yaml') else ProjectConfig.from_txt(config_file)
    workflow = AutoSHUDWorkflow(config)
    workflow.visualize_results()


@main.command()
@click.argument('output_file', type=click.Path(), default='project.yaml')
def init(output_file):
    """Create a template configuration file"""
    template = """# pyAutoSHUD Project Configuration

project:
  name: "MyProject"
  start_year: 2017
  end_year: 2018
  output_dir: "./output"

data:
  # Input data paths
  dem: "data/elevation.tif"
  watershed_boundary: "data/wbd.shp"
  stream_network: "data/stm.shp"
  lake: null  # Optional

  # Soil data configuration
  soil:
    source: "isric"  # Options: isric, ssurgo, local
    data_dir: "/path/to/soil/data"
    # For local source:
    # file: "data/soil.tif"
    # table: "data/soil_params.csv"

  # Land cover configuration
  landcover:
    source: "glc"  # Options: glc, nlcd, local
    file: "/path/to/landcover.tif"
    # table: "data/landcover_params.csv"  # For local source

  # Meteorological forcing data
  forcing:
    source: "gldas"  # Options: gldas, nldas, cmfd, cmip6, fldas, local
    data_dir: "/path/to/forcing/data"
    output_dir: "./output/forcing"

model:
  # Mesh generation parameters
  num_cells: 1000
  max_area_km2: 10.0
  min_angle: 31.0

  # Hydrological parameters
  aquifer_depth: 20.0
  buffer_distance: 5000.0

  # River parameters (optional, auto-calculated if not specified)
  # river_width: 5.0
  # river_depth: 1.0

simulation:
  start_day: 0
  end_day: 365  # Optional, auto-calculated from years if not specified
  solver_step: 2
  cryosphere: false

# Calibration configuration (optional)
calibration:
  algorithm: "NSGA2"  # Options: NSGA2, PSO, SCE-UA, DDS
  iterations: 100
  objective: ["NSE", "RMSE"]
  observed_data: "data/observed_discharge.csv"

  parameters:
    - name: "GEOL_KSATH"
      min: 0.1
      max: 10.0
    - name: "SOIL_KINF"
      min: 0.001
      max: 1.0
    - name: "RIV_ROUGH"
      min: 0.01
      max: 0.5
"""

    with open(output_file, 'w') as f:
        f.write(template)

    logger.info(f"Created template configuration file: {output_file}")
    logger.info("Please edit the file and update paths according to your data")


if __name__ == '__main__':
    main()
