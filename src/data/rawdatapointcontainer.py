# -*- coding: utf-8 -*-
"""
Created on Mon May 12 13:36:39 2025

@author: kaisjuli
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .abstractrawdatapoint import AbstractRawDataPoint
    from numpy import array
    
from .mpms3rawdatapoint import MPMS3RawDataPoint
from .mpmsrawdatapoint import MPMSRawDataPoint
    
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
        self.container : list[AbstractRawDataPoint] = []
        
    def add(self, info : str | dict[str, float], data : list[str] | array, device : str) -> None:
        '''
        Creates a new RawDataPoint and adds it to the container.

        Parameters
        ----------
        info : str | None
            The secondary information about the datapoint in the raw file.
        data : list[str] | array
            The measured data of the scan.

        Returns
        -------
        None.

        '''
        if device == "MPMS3":
            self.container.append(MPMS3RawDataPoint(info, data))
        elif device == "MPMS":
            self.container.append(MPMSRawDataPoint(info, data))
        
    def remove(self, rawdatapoint : AbstractRawDataPoint) -> None:
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
        
    def __getitem__(self, index) -> AbstractRawDataPoint:
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