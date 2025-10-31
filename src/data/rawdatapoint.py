# -*- coding: utf-8 -*-
"""
Created on Mon May 12 11:02:29 2025

@author: kaisjuli
"""
import numpy as np
from numpy.polynomial.polynomial import Polynomial as poly

class RawDataPoint():
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
    
    def __init__(self, info_str : str, data_list : list[str]) -> None:
        self.jump_corrected : bool = False
        self.scan_direction : str = "up"
        
        self.__convert_info_string__(info_str)
        self.__convert_data_list__(data_list)
        return
    
    def __convert_info_string__(self, info_string : str) -> None:
        '''
        Unzips the info_string into the corresponding informations.

        Parameters
        ----------
        info_string : str
            The encoded secundary information about the datapoint.

        Returns
        -------
        None.

        '''
        def get_info_element(info_list : list[str], key : str, with_unit : bool = True) -> float:
            '''
            Gets the information about the specific key with or without the unit from the info_list.

            Parameters
            ----------
            info_list : list[str]
                A list of encoded secundary information about the datapoint.
            key : str
                The key to be search after.
            with_unit : bool, optional
                Determines if the information comes with a unit. The default is True.

            Returns
            -------
            float
                The specific information from the key.

            '''
            result : str = [sub for sub in info_list if key in sub][0]
            return float(result.split(" ")[-1 - int(with_unit)].replace("=", ""))
        
        info_string_splitted : list[str] = info_string.split(";")
        self.low_temp : float = get_info_element(info_string_splitted, "low temp")
        self.high_temp : float = get_info_element(info_string_splitted, "high temp")
        self.avg_temp : float = get_info_element(info_string_splitted, "avg. temp")
        self.low_field : float = get_info_element(info_string_splitted, "low field")
        self.high_field : float = get_info_element(info_string_splitted, "high field")
        self.drift : float = get_info_element(info_string_splitted, "drift")
        self.slope : float = get_info_element(info_string_splitted, "slope")
        self.squid_range : float = get_info_element(info_string_splitted, "squid range", False)
        self.given_center : float = get_info_element(info_string_splitted, "given center")
        self.calculated_center : float = get_info_element(info_string_splitted, "calculated center")
        self.amp_fixed : float = get_info_element(info_string_splitted, "amp fixed")
        self.amp_free : float = get_info_element(info_string_splitted, "amp free")
        
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
        
    def __convert_data_list__(self, data_list : list[str]) -> None:
        '''
        Converts the given data_list to a numpy array with increasing raw positions.

        Parameters
        ----------
        data_list : list[str]
            The encoded data_list from the raw file.

        Returns
        -------
        None.

        '''
        self.data : np.ndarray = np.array(data_list, dtype=float)
        if self.data[0, 1] - self.data[-1, 1] > 0:
            self.scan_direction : str = "down"
        self.data : np.ndarray = self.data[self.data[:, 1].argsort(), :]
        self.__correct_jumps__()
        
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
        return self.data[:, 1]
    
    @property
    def raw_voltage(self) -> np.ndarray:
        '''
        Returns the raw voltages of the scan.

        Returns
        -------
        np.ndarray
            The raw voltages of the scan.

        '''
        return self.data[:, 2] * self.squid_range
    
    @property
    def processed_voltage(self) -> np.ndarray:
        '''
        Returns the processed voltages of the scan.

        Returns
        -------
        np.ndarray
            The processed voltages of the scan.

        '''
        return self.data[:, 3]
    
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
