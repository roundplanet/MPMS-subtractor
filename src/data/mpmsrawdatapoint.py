# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:06:35 2026

@author: kaisjuli
"""

import numpy as np
from numpy.polynomial.polynomial import Polynomial as poly

from .abstractrawdatapoint import AbstractRawDataPoint

class MPMSRawDataPoint(AbstractRawDataPoint):
    """
    A class to represent a datapoint in a raw file.
    
    Parameters
    ----------
    info_str : str
        The secondary information about the datapoint in the raw file.
    data_list : list[str]
        The measured data of the scan.
        
    Attributes
    ----------
    low_temp : float
        The lowest temperature in K during the scan.
    high_temp : float
        The highest temperature in K during the scan.
    avg_temp : float
        The average temperature in K during the scan.
    low_field : float
        The lowest field in Oe during the scan.
    high_field : float
        The highest field in Oe during the scan.
    drift : float
        The drift in V/s during the scan.
    slope : float
        The slope of the scan in V/mm.
    squid_range : float
        The used range of the squid during the scan.
    given_center : float
        The given center of the scan in mm.
    calculated_center : float
        The calculated center of the scan in mm.
    amp_fixed : float
        The calculated amplitude of the scan from the detected signal
        with a fixed center in V.
    amp_free : float
        The calculated amplitude of the scan from the detected signal
        with a free center in V.
    
    jump_corrected : bool
        If the scan contains a jump in the signal, which was corrected.
    scan_direction : str
        States if the scan was performed moving 'up' or 'down'.
    data : np.ndarray
        The converted data from the data_list.
    temperature : np.ndarray
        The mean of the high and low temperature in K.
    field : np.ndarray
        The mean of the high and low field in Oe.
    timestamp : np.ndarray
        The timestamps of the scan.
    raw_position : np.ndarray
        The raw positions of the scan.
    raw_voltage : np.ndarray
        The raw voltage of the scan weight with the squid range factor.
    processed_voltage : np.ndarray
        The processed voltage of the scan.
    """
    
    def __init__(self, info : dict[str, float], data : np.array) -> None:
        super().__init__("MPMS3")
        self.jump_corrected : bool = False
        self.scan_direction : str = "up"
        
        gain_mapping : list[float] = [1, 2, 5, 10]
        self.squid_range : float = 10**(info["RANGE"] - 1) / gain_mapping[info["GAIN"]]
        print(info, self.squid_range)
        
        self.data : np.array = data
        self.__correct_jumps__()
        self.__convert_info_from_data__()
        return
    
    def __convert_info_from_data__(self) -> None:
        '''
        Extracts the secundary information out of the provided data

        Returns
        -------
        None.

        '''
        
        self.low_temp : float = np.min(self.data[:, 2:4])
        self.high_temp : float = np.max(self.data[:, 2:4])
        self.avg_temp : float = (self.low_temp + self.high_temp) / 2
        self.low_field : float = np.min(self.data[:, 1])
        self.high_field : float = np.max(self.data[:, 1])
        self.drift : float = 0.0
        self.slope : float = 0.0
        self.given_center : float = np.max(self.data[:, -3]) / 2
        self.calculated_center : float = np.max(self.data[:, -3]) / 2
        self.amp_fixed : float = 0.0
        self.amp_free : float = 0.0
        
    def print_info(self) -> None:
        '''
        Prints all secundary information about the datapoint.

        Returns
        -------
        None.

        '''
        s : str = "low temp = {} K\n".format(self.low_temp)
        s += "high temp = {} K\n".format(self.high_temp)
        s += "avg. temp = {} K\n".format(self.avg_temp)
        s += "low field = {} Oe\n".format(self.low_field)
        s += "high field = {} Oe\n".format(self.high_field)
        s += "drift = {} V/s\n".format(self.drift)
        s += "slope = {} V/mm\n".format(self.slope)
        s += "squid range = {}\n".format(self.squid_range)
        s += "given center = {} mm\n".format(self.given_center)
        s += "calculated center = {} mm\n".format(self.calculated_center)
        s += "amp fixed = {} V\n".format(self.amp_fixed)
        s += "amp free = {} V\n".format(self.amp_free)
        print(s)
        
    def __correct_jumps__(self) -> None:
        '''
        Corrects possible jumps in the voltage signal.

        Returns
        -------
        None.

        '''
        self.data : np.ndarray = self.data[np.abs(self.data[:, 2]) < 500, :]

        mean_diff : float = np.mean(np.abs(np.diff(self.data[:, 2])))
        jump_index : np.ndarray = np.argwhere(np.abs(np.diff(self.data[:, 2])) > 10 * mean_diff)

        for index in jump_index.flatten():
            self.jump_corrected : bool = True
            if index > 9:
                fit_data : np.ndarray = self.data[index-9:index+1, 1:3]
                fit_func : poly = np.polynomial.Polynomial.fit(fit_data[:, 0], fit_data[:, 1], 2)
                y_goal : np.ndarray = fit_func(self.data[index+1, 1])
                self.data[index+1:, 2] += y_goal - self.data[index+1, 2]
            else:
                fit_data : np.ndarray = self.data[index+1:index+11, 1:3]
                fit_func : poly = np.polynomial.Polynomial.fit(fit_data[:, 0], fit_data[:, 1], 2)
                y_goal : np.ndarray = fit_func(self.data[index, 1])
                self.data[:index, 2] += y_goal - self.data[index, 2]
                
        
    @property
    def timestamp(self) -> np.ndarray:
        '''
        Returns the timestamps of the scan.

        Returns
        -------
        np.ndarray
            The timestamps of the scan.

        '''
        return self.data[:, 0]
    
    @property
    def raw_position(self) -> np.ndarray:
        '''
        Returns the raw positions of the scan.

        Returns
        -------
        np.ndarray
            The raw positions of the scan.

        '''
        return self.data[:, 4]
    
    @property
    def raw_voltage(self) -> np.ndarray:
        '''
        Returns the raw voltages of the scan.

        Returns
        -------
        np.ndarray
            The raw voltages of the scan.

        '''
        return self.data[:, -2] * self.squid_range
    
    @property
    def processed_voltage(self) -> np.ndarray:
        '''
        Returns the processed voltages of the scan.

        Returns
        -------
        np.ndarray
            The processed voltages of the scan.

        '''
        return self.data[:, -1]
    
    @property
    def temperature(self) -> float:
        '''
        Returns the mean temperature of the scan.

        Returns
        -------
        np.ndarray
            The mean temperature of the scan.

        '''
        return (self.high_temp + self.low_temp) / 2
    
    @property
    def field(self) -> float:
        '''
        Returns the mean field of the scan.

        Returns
        -------
        np.ndarray
            The mean field of the scan.

        '''
        return (self.high_field + self.low_field) / 2
