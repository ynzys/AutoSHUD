"""
IO module for SHUD input/output files
Ensures compatibility with SHUD C++ core program
"""

from .shud_io import (
    write_mesh,
    write_river,
    write_attribute,
    write_river_segment,
    write_landcover,
    write_soil,
    write_geology,
    write_initial_condition,
    write_parameter,
    write_calibration,
    write_time_series,
    read_output,
    SHUDFiles,
)

__all__ = [
    "write_mesh",
    "write_river",
    "write_attribute",
    "write_river_segment",
    "write_landcover",
    "write_soil",
    "write_geology",
    "write_initial_condition",
    "write_parameter",
    "write_calibration",
    "write_time_series",
    "read_output",
    "SHUDFiles",
]
