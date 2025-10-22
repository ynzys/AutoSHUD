"""
SHUD model runner - compile and execute SHUD
"""
from pathlib import Path
import subprocess
import shutil
from loguru import logger

from ..config import ProjectConfig


class SHUDRunner:
    """SHUD model runner"""

    def __init__(self, config: ProjectConfig):
        self.config = config
        self.shud_src_dir = Path('shud_src')
        self.shud_executable = Path('shud')

    def compile(self):
        """Compile SHUD from source"""
        logger.info("Compiling SHUD...")

        if not self.shud_src_dir.exists():
            self._download_shud()

        # Install SUNDIALS if needed
        self._install_sundials()

        # Compile SHUD
        self._compile_shud()

        logger.success("SHUD compiled successfully")

    def run(self, silent: bool = False):
        """
        Run SHUD simulation

        Args:
            silent: Suppress output
        """
        logger.info(f"Running SHUD simulation: {self.config.name}")

        # Ensure SHUD is compiled
        if not self.shud_executable.exists():
            logger.warning("SHUD executable not found, compiling...")
            self.compile()

        # Copy executable to model directory
        model_exec = self.config.model_input_dir / 'shud'
        shutil.copy(self.shud_executable, model_exec)

        # Run SHUD
        cmd = [str(model_exec), self.config.name]
        logger.info(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.config.model_input_dir,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )

            if result.returncode == 0:
                logger.success("SHUD simulation completed")

                # Save log
                log_file = self.config.model_output_dir / f'{self.config.name}.log'
                with open(log_file, 'w') as f:
                    f.write(result.stdout)

                if not silent:
                    logger.info(f"Log saved to: {log_file}")
            else:
                logger.error(f"SHUD simulation failed: {result.stderr}")
                raise RuntimeError(f"SHUD failed with return code {result.returncode}")

        except subprocess.TimeoutExpired:
            logger.error("SHUD simulation timed out")
            raise

    def _download_shud(self):
        """Download SHUD source from GitHub"""
        logger.info("Downloading SHUD source from GitHub...")

        cmd = [
            'git', 'clone',
            'https://github.com/SHUD-System/SHUD.git',
            str(self.shud_src_dir)
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info("SHUD source downloaded")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download SHUD: {e}")
            raise

    def _install_sundials(self):
        """Install SUNDIALS dependency"""
        logger.info("Installing SUNDIALS...")

        configure_script = self.shud_src_dir / 'configure'

        if configure_script.exists():
            try:
                subprocess.run(
                    [str(configure_script)],
                    cwd=self.shud_src_dir,
                    check=True,
                    capture_output=True
                )
                logger.info("SUNDIALS installed")
            except subprocess.CalledProcessError as e:
                logger.warning(f"SUNDIALS installation may have issues: {e}")
        else:
            logger.warning("Configure script not found, skipping SUNDIALS installation")

    def _compile_shud(self):
        """Compile SHUD using make"""
        logger.info("Compiling SHUD with make...")

        try:
            # Clean previous build
            subprocess.run(
                ['make', 'clean'],
                cwd=self.shud_src_dir,
                capture_output=True
            )

            # Compile
            result = subprocess.run(
                ['make', 'shud'],
                cwd=self.shud_src_dir,
                check=True,
                capture_output=True,
                text=True
            )

            # Copy executable
            src_exec = self.shud_src_dir / 'shud'
            if src_exec.exists():
                shutil.copy(src_exec, self.shud_executable)
                logger.info(f"SHUD executable: {self.shud_executable}")
            else:
                raise FileNotFoundError("SHUD executable not found after compilation")

        except subprocess.CalledProcessError as e:
            logger.error(f"Compilation failed: {e.stderr}")
            raise
