"""Pytest configuration"""
import pytest
from pathlib import Path


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project directory"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create subdirectories
    (project_dir / "input").mkdir()
    (project_dir / "output").mkdir()
    (project_dir / "DataPre").mkdir()

    return project_dir


@pytest.fixture
def sample_config():
    """Sample project configuration"""
    return {
        'project': {
            'name': 'TestProject',
            'start_year': 2017,
            'end_year': 2017,
            'output_dir': './test_output'
        },
        'model': {
            'num_cells': 100,
            'max_area_km2': 1.0,
            'aquifer_depth': 10.0
        }
    }
