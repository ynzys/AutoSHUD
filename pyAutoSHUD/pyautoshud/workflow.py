"""
Main workflow orchestration
"""
from pathlib import Path
from loguru import logger

from .config import ProjectConfig
from .data import DEMProcessor, SoilProcessor, LandcoverProcessor, ForcingProcessor
from .mesh import MeshGenerator
from .model import SHUDModelBuilder
from .runner import SHUDRunner
from .analysis import WaterBalanceAnalyzer, ResultVisualizer
from .calibration import ModelCalibrator


class AutoSHUDWorkflow:
    """Main workflow class for AutoSHUD"""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.config.create_directories()

    def run_all(self, skip_preprocessing=False, skip_model_build=False, skip_simulation=False):
        """Run complete workflow"""

        if not skip_preprocessing:
            logger.info("Step 1: Data Preprocessing")
            self.preprocess_data()

        if not skip_model_build:
            logger.info("Step 2: Model Building")
            self.build_model()

        if not skip_simulation:
            logger.info("Step 3: Compile and Run SHUD")
            self.compile_shud()
            self.run_simulation()

        logger.info("Step 4: Post-processing")
        self.analyze_results()
        self.visualize_results()

        logger.success("Workflow completed successfully!")

    def preprocess_data(self):
        """Preprocess all input data"""
        logger.info("Processing DEM and watershed boundary...")
        dem_proc = DEMProcessor(self.config)
        dem_proc.process()

        logger.info("Processing soil data...")
        soil_proc = SoilProcessor(self.config)
        soil_proc.process()

        logger.info("Processing land cover data...")
        lc_proc = LandcoverProcessor(self.config)
        lc_proc.process()

        logger.info("Processing forcing data...")
        forcing_proc = ForcingProcessor(self.config)
        forcing_proc.process()

    def build_model(self):
        """Build SHUD model"""
        logger.info("Generating mesh...")
        mesh_gen = MeshGenerator(self.config)
        mesh = mesh_gen.generate()

        logger.info("Building SHUD model input files...")
        builder = SHUDModelBuilder(self.config)
        builder.build(mesh)

    def compile_shud(self):
        """Compile SHUD"""
        runner = SHUDRunner(self.config)
        runner.compile()

    def run_simulation(self):
        """Run SHUD simulation"""
        runner = SHUDRunner(self.config)
        runner.run()

    def analyze_results(self):
        """Analyze simulation results"""
        analyzer = WaterBalanceAnalyzer(self.config)
        analyzer.analyze()

    def visualize_results(self):
        """Visualize results"""
        visualizer = ResultVisualizer(self.config)
        visualizer.plot_all()

    def calibrate(self, algorithm='NSGA2', iterations=100, output_file='calibration.csv'):
        """Run model calibration"""
        calibrator = ModelCalibrator(self.config, algorithm=algorithm)
        results = calibrator.calibrate(iterations=iterations)
        results.to_csv(output_file)
        logger.success(f"Calibration completed. Results saved to {output_file}")

    def run_step(self, step_name: str):
        """Run specific step"""
        steps = {
            'preprocess': self.preprocess_data,
            'build': self.build_model,
            'compile': self.compile_shud,
            'simulate': self.run_simulation,
            'analyze': self.analyze_results,
            'visualize': self.visualize_results,
        }

        if step_name in steps:
            logger.info(f"Running step: {step_name}")
            steps[step_name]()
        else:
            logger.error(f"Unknown step: {step_name}")
            logger.info(f"Available steps: {', '.join(steps.keys())}")
