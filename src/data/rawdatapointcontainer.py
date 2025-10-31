# -*- coding: utf-8 -*-
"""
Created on Mon May 12 13:36:39 2025

@author: kaisjuli
"""
from .rawdatapoint import RawDataPoint
    
class RawDataPointContainer():
    """
    A class to store all datapoints of a raw datafile.
    
    Parameters
    ----------
    
        
    Attributes
    ----------
    container : list[RawDataPoint]
        Contains all datapoints of the raw datafile.
    """
    
    def __init__(self) -> None:
        self.container : list[RawDataPoint] = []
        
    def add(self, info_str : str, data_list : list[str]) -> None:
        '''
        Creates a new RawDataPoint and adds it to the container.

        Parameters
        ----------
        info_str : str
            The secondary information about the datapoint in the raw file.
        data_list : list[str]
            The measured data of the scan.

        Returns
        -------
        None.

        '''
        self.container.append(RawDataPoint(info_str, data_list))
        
    def remove(self, rawdatapoint : RawDataPoint) -> None:
        '''
        Removes an existing RawDataPoint from the container.

        Parameters
        ----------
        rawdatapoint : RawDataPoint
            The datapoint to remove.

        Returns
        -------
        None.

        '''
        self.container.remove(rawdatapoint)
        
    def __getitem__(self, index) -> RawDataPoint:
        '''
        Gets the datapoint from the container at the desired position.

        Parameters
        ----------
        index : int
            The desired position in the container.

        Returns
        -------
        RawDataPoint
            The raw datapoint at the specified position.

        '''
        return self.container[index]
    
    def __len__(self) -> int:
        '''
        Returns the amount of raw datapoints inside the container.

        Returns
        -------
        int
            The amount of raw datapoints inside the container.

        '''
        return len(self.container)