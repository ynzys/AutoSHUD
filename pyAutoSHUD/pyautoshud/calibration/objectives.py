"""
Objective functions for model calibration
"""
import numpy as np
from typing import Tuple


def NSE(observed: np.ndarray, simulated: np.ndarray) -> float:
    """
    Nash-Sutcliffe Efficiency

    Args:
        observed: Observed values
        simulated: Simulated values

    Returns:
        NSE value (higher is better, max = 1.0)
    """
    obs_mean = np.mean(observed)
    numerator = np.sum((observed - simulated) ** 2)
    denominator = np.sum((observed - obs_mean) ** 2)

    if denominator == 0:
        return 0.0

    return 1.0 - (numerator / denominator)


def RMSE(observed: np.ndarray, simulated: np.ndarray) -> float:
    """
    Root Mean Square Error

    Args:
        observed: Observed values
        simulated: Simulated values

    Returns:
        RMSE value (lower is better)
    """
    return np.sqrt(np.mean((observed - simulated) ** 2))


def KGE(observed: np.ndarray, simulated: np.ndarray) -> float:
    """
    Kling-Gupta Efficiency

    Args:
        observed: Observed values
        simulated: Simulated values

    Returns:
        KGE value (higher is better, max = 1.0)
    """
    # Correlation coefficient
    r = np.corrcoef(observed, simulated)[0, 1]

    # Relative variability
    alpha = np.std(simulated) / np.std(observed)

    # Relative mean
    beta = np.mean(simulated) / np.mean(observed)

    # KGE
    kge = 1.0 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)

    return kge


def PBIAS(observed: np.ndarray, simulated: np.ndarray) -> float:
    """
    Percent Bias

    Args:
        observed: Observed values
        simulated: Simulated values

    Returns:
        PBIAS value (0 is perfect, positive means underestimation)
    """
    return 100.0 * np.sum(observed - simulated) / np.sum(observed)


def R2(observed: np.ndarray, simulated: np.ndarray) -> float:
    """
    Coefficient of Determination

    Args:
        observed: Observed values
        simulated: Simulated values

    Returns:
        R² value (higher is better, max = 1.0)
    """
    return np.corrcoef(observed, simulated)[0, 1] ** 2


def calculate_metrics(observed: np.ndarray, simulated: np.ndarray) -> dict:
    """
    Calculate all common metrics

    Args:
        observed: Observed values
        simulated: Simulated values

    Returns:
        Dictionary of metric values
    """
    return {
        'NSE': NSE(observed, simulated),
        'RMSE': RMSE(observed, simulated),
        'KGE': KGE(observed, simulated),
        'PBIAS': PBIAS(observed, simulated),
        'R2': R2(observed, simulated),
    }
