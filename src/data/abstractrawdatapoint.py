# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 15:51:23 2026

@author: kaisjuli
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import numpy as np
    
class AbstractRawDataPoint():
    
    def __init__(self, device : str) -> None:
        self.device : str = device
        
    @property
    def timestamp(self) -> np.ndarray:
        '''
        Returns the timestamps of the scan.

        Returns
        -------
        np.ndarray
            The timestamps of the scan.

        '''
        raise NotImplementedError
    
    @property
    def raw_position(self) -> np.ndarray:
        '''
        Returns the raw positions of the scan.

        Returns
        -------
        np.ndarray
            The raw positions of the scan.

        '''
        raise NotImplementedError
    
    @property
    def raw_voltage(self) -> np.ndarray:
        '''
        Returns the raw voltages of the scan.

        Returns
        -------
        np.ndarray
            The raw voltages of the scan.

        '''
        raise NotImplementedError
    
    @property
    def temperature(self) -> float:
        '''
        Returns the mean temperature of the scan.

        Returns
        -------
        np.ndarray
            The mean temperature of the scan.

        '''
        raise NotImplementedError
    
    @property
    def field(self) -> float:
        '''
        Returns the mean field of the scan.

        Returns
        -------
        np.ndarray
            The mean field of the scan.

        '''
        raise NotImplementedError
