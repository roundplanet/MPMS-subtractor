# -*- coding: utf-8 -*-
"""
Created on Thu May 15 08:38:56 2025

@author: kaisjuli
"""
from .measurement import Measurement

class MeasurementContainer():
    """
    A class to store multiple measurements.
    
    Parameters
    ----------
    
        
    Attributes
    ----------
    container : list[RawDataPoint]
        Contains all measurements.
    """
    
    def __init__(self) -> None:
        self.container : list[Measurement] = []
        
    def add(self, sample_filename : str, background_filename : None | str, 
            direct_mapping : bool = True) -> Measurement:
        '''
        Creates a new measurement and adds it to the container.

        Parameters
        ----------
        sample_filename : str
            The filename to the sample measurement.
        background_filename : None | str
            The filename to the background measurement.
        direct_mapping : bool, optional
            If the mapping should be direct or indirect. The default is True.

        Returns
        -------
        Measurement
            The created measurement.

        '''
        measurement : Measurement = Measurement(sample_filename, background_filename, direct_mapping)
        self.container.append(measurement)
        return measurement
        
    def remove(self, measurement : Measurement) -> None:
        '''
        Removes an existing measurement from the container.

        Parameters
        ----------
        measurement : Measurement
            The measurement to remove.

        Returns
        -------
        None.

        '''
        self.container.remove(measurement)
        
    def get_from_filename(self, filename : str) -> Measurement:
        '''
        Returns the measurement to the corresponding filename.

        Parameters
        ----------
        filename : str
            The filename to search for.

        Returns
        -------
        Measurement
            The matching measurement.

        '''
        for measurement in self.container:
            if filename == measurement.sample_rdf.filename.split("/")[-1]:
                return measurement
        
    def __getitem__(self, index) -> Measurement:
        '''
        Gets the measurement from the container at the desired position.

        Parameters
        ----------
        index : int
            The desired position in the container.

        Returns
        -------
        RawDataPoint
            The measurement at the specified position.

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