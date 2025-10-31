# -*- coding: utf-8 -*-
"""
Created on Mon May 12 16:25:08 2025

@author: kaisjuli
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..data import RawDataPoint
    
import numpy as np

def subtract_background(sample_rdp : RawDataPoint, background_rdp : RawDataPoint) -> tuple(np.ndarray, np.ndarray):
    '''
    Subtracts the background signal from a raw datapoint. The positions of the moment are interpolated
    between the maximum shared boundaries.
    
    Paramters
    ----------
    samle_rdp : RawDataPoint
        The raw datapoint of the measurement with the sample.
    background_rdp : RawDataPoint
        The raw datapoint of the background measurement.
    
    Returns
    --------
    tuple(np.ndarray, np.ndarray)
        The interpolated position of the moment and the subtracted voltage signal.
    '''
    min_pos : float = max([np.min(sample_rdp.raw_position), np.min(background_rdp.raw_position)])
    max_pos : float = min([np.max(sample_rdp.raw_position), np.max(background_rdp.raw_position)])
    positions : np.ndarray = np.linspace(min_pos, max_pos, len(sample_rdp.raw_position))
    sample_interp : np.ndarray = np.interp(positions, sample_rdp.raw_position, sample_rdp.raw_voltage)
    background_interp : np.ndarray = np.interp(positions, background_rdp.raw_position, background_rdp.raw_voltage)
    return positions, sample_interp - background_interp