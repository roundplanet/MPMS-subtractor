# -*- coding: utf-8 -*-
"""
Created on Mon May 12 13:55:18 2025

@author: kaisjuli
"""
import numpy as np
from scipy.optimize import curve_fit

from ..constants import COIL_RADIUS, COIL_DISTANCE, SYSTEM_CALIBRATION, DC_CALIBRATION_FACTOR

def gradiometer_function(z : float, A : float, S : float, m : float, C : float) -> float:
    '''
    The theoretical function of a magnetic pointlike dipol crossing a second gradiometer. The
    radius of the coils and the distance between them is defined in the constant file.

    Parameters
    ----------
    z : float
        The position of the dipole.
    A : float
        The amplitude of the signal.
    S : float
        The veritcal shift of the signal.
    m : float
        The slope of the signal.
    C : float
        The center of the signal.

    Returns
    -------
    float
        The generated signal at the given position of the dipole.

    '''
    voltage = 2 * COIL_RADIUS**2 * (COIL_RADIUS**2 + (z - C)**2)**(-3/2)
    voltage -=  COIL_RADIUS**2 * (COIL_RADIUS**2 + ( COIL_DISTANCE + z - C)**2)**(-3/2)
    voltage -=  COIL_RADIUS**2 * (COIL_RADIUS**2 + (-COIL_DISTANCE + z - C)**2)**(-3/2)
    return S + A * voltage + m * z

def gradiometer_function_fixed_center(C : float) -> callable:
    '''
    The theoretical function of a magnetic pointlike dipol crossing a second gradiometer
    at a fixed center.

    Parameters
    ----------
    C : float
        The fixed center.

    Returns
    -------
    callable
        The gradiometer fucntion with a fixed center.

    '''
    def gradiometer_function(z : float, A : float, S : float, m : float) -> float:
        '''
        The theoretical function of a magnetic pointlike dipol crossing a second gradiometer. The
        radius of the coils and the distance between them is defined in the constant file.

        Parameters
        ----------
        z : float
            The position of the dipole.
        A : float
            The amplitude of the signal.
        S : float
            The veritcal shift of the signal.
        m : float
            The slope of the signal.
        C : float
            The center of the signal.

        Returns
        -------
        float
            The generated signal at the given position of the dipole.

        '''
        voltage = 2 * COIL_RADIUS**2 * (COIL_RADIUS**2 + (z - C)**2)**(-3/2)
        voltage -=  COIL_RADIUS**2 * (COIL_RADIUS**2 + ( COIL_DISTANCE + z - C)**2)**(-3/2)
        voltage -=  COIL_RADIUS**2 * (COIL_RADIUS**2 + (-COIL_DISTANCE + z - C)**2)**(-3/2)
        return S + A * voltage + m * z
    return gradiometer_function

def fit_signal(position : np.ndarray,
               voltage : np.ndarray,
               p0 : None | list[float] = None,
               fixed_center : bool = False,
               center_pos : float = 0.0
               ) -> list[np.ndarray]:
    '''
    Fits the signal to the theoretical function of of a magnetic pointlike dipol crossing
    a second gradiometer.

    Parameters
    ----------
    position : np.ndarray
        The position of the dipole.
    voltage : np.ndarray
        The generated voltage of the dipole.
    p0 : None | list[float], optional
        The initial starting condition for the fit. The default is None.
    fixed_center : bool, optional
        If the fit is performed with a fixed center of the signal. The default is False.
    center_pos : float, optional
        The fixed center of the signal. The default is 0.0.

    Returns
    -------
    result : list[np.ndarray]
        The fitting result.

    '''
    if p0 is None:
        p0 : list[float] = [0, np.mean(voltage), 0, 37]
    if fixed_center:
        result = curve_fit(gradiometer_function_fixed_center(center_pos), position, voltage, p0=p0[:3])
    else:
        result = curve_fit(gradiometer_function, position, voltage, p0=p0)
    return result

def convert_amplitude_to_moment(amplitude : float) -> float:
    '''
    Converts the fitted ampliutde to the corresponding moment value. The corresponding
    calibration factors are defined in the constants file.

    Parameters
    ----------
    amplitude : float
        The fitted amplitude of the signal.

    Returns
    -------
    float
        The converted moment.

    '''
    return - SYSTEM_CALIBRATION * DC_CALIBRATION_FACTOR * amplitude / 1000