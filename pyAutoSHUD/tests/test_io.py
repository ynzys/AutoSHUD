"""Test IO module"""
import pytest
import pandas as pd
from pathlib import Path
import tempfile
from pyautoshud.io import write_mesh, write_soil, write_parameter


def test_write_mesh():
    """Test mesh file writing"""
    mesh_df = pd.DataFrame({
        'ID': [1, 2],
        'Node1': [1, 2],
        'Node2': [2, 3],
        'Node3': [3, 4],
        'Nabr1': [2, 1],
        'Nabr2': [0, 0],
        'Nabr3': [0, 0],
        'Zmax': [100.0, 120.0]
    })

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.mesh') as f:
        write_mesh(mesh_df, f.name)
        assert Path(f.name).exists()

        # Verify format
        with open(f.name, 'r') as rf:
            lines = rf.readlines()
            assert lines[0].strip() == '2\t8'
            assert 'ID' in lines[1]


def test_write_soil():
    """Test soil parameter file writing"""
    soil_df = pd.DataFrame({
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

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.soil') as f:
        write_soil(soil_df, f.name)
        assert Path(f.name).exists()


def test_write_parameter():
    """Test parameter file writing"""
    params = {
        'VERBOSE': 0,
        'INIT_MODE': 3,
        'START': 0,
        'END': 365
    }

    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.para') as f:
        write_parameter(params, f.name)
        assert Path(f.name).exists()

        # Verify format
        with open(f.name, 'r') as rf:
            content = rf.read()
            assert 'VERBOSE\t0' in content
            assert 'START\t0' in content
