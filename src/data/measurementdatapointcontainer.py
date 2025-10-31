# -*- coding: utf-8 -*-
"""
Created on Wed May 14 08:39:27 2025

@author: kaisjuli
"""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .rawdatapoint import RawDataPoint
    
from .measurementdatapoint import MeasurementDataPoint
    
class MeasurementDataPointContainer():
    """
    A class to store all measurement datapoints of a measurement.
    
    Parameters
    ----------
    
        
    Attributes
    ----------
    container : list[MeasurementDataPoint]
        Contains all datapoints of the measurement.
    """
    
    def __init__(self) -> None:
        self.container : list[MeasurementDataPoint] = []
        
    def add(self, sample_rdp : RawDataPoint, background_rdp : RawDataPoint) -> None:
        '''
        Creates a new MeasurementDataPoint and adds it to the container, if fitting
        is possible.

        Parameters
        ----------
        sample_rdp : RawDataPoint
            The raw datapoint of the sample.
        background_rdp : RawDataPoint
            The raw datapoint of the background.

        Returns
        -------
        None.

        '''
        try:
            self.container.append(MeasurementDataPoint(sample_rdp, background_rdp))
        except RuntimeError:
            print("fitting not possible")
            pass
        
    def remove(self,  measurementdatapoint : MeasurementDataPoint) -> None:
        '''
        Removes an existing MeasurementDataPoint from the container.

        Parameters
        ----------
        measurementdatapoint : MeasurementDataPoint
            The measurement datapoint to remove.

        Returns
        -------
        None.

        '''
        self.container.remove(measurementdatapoint)
        
    def __getitem__(self, index) -> MeasurementDataPoint:
        '''
        Gets the measurement datapoint from the container at the desired position.

        Parameters
        ----------
        index : int
            The desired position in the container.

        Returns
        -------
        MeasurementDataPoint
            The measurement datapoint at the specified position.

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