# -*- coding: utf-8 -*-
"""
Created on Wed May 14 08:08:51 2025

@author: kaisjuli
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .measurementdatapoint import MeasurementDataPoint
    from .rawdatapoint import RawDataPoint
    
import numpy as np

from .rawdatafile import RawDataFile    
from .measurementdatapointcontainer import MeasurementDataPointContainer

class Measurement():
    """
    A class to represent a measurement and provide methods to access the fitted data.
    
    Parameters
    ----------
    sample_rdp : RawDataPoint | None
        The raw datapoint of the sample. The default is None.
    background_rdp : RawDataPoint | None
        The raw datapoint of the background. The default is None.
    direct_mapping : bool
        If the background should be directly mapped on the sample or indirectly.
        The default is True.
        
    Attributes
    ----------
    name : str
        The name of the measurement.
    sample_rdf : RawDataFile
        The raw datafile of the sample measurement.
    background_rdf : RawDataFile
        The raw datafile of the background measurement.
    datapoints : MeasurementDataPointContainer
        The container of all measurement datapoints.
    
    nr_not_matching_datapoints : int
        The number of sample datapoints which don't have a matching background datapoint.
    nr_jump_corrected_datapoints : int
        The number of datapoints which had to be corrected due to jumps in the voltage signal.
        
    timestamp : np.ndarray
        The timestamps of the measurement.
    temperature : np.ndarray
        The temperatures of the measurement.
    field : np.ndarray
        The fields of the measurement.
    moment : np.ndarray
        The moments of the measurement.
    volume_susceptibility : np.ndarray
        The volume susceptibility of the measurement.
    mass_susceptibility : np.ndarray
        The mass susceptibility of the measurement.
    molar_susceptibility : np.ndarray
        The molar susceptibility of the measurement.
    moment_fixed_ctr : np.ndarray
        The moment of the measurement with a fixed center.
    volume_susceptibility_fixed_ctr : np.ndarray
        The volume susceptibility of the measurement with a fixed center.
    mass_susceptibility_fixed_ctr : np.ndarray
        The mass susceptibility of the measurement with a fixed center.
    molar_susceptibility_fixed_ctr : np.ndarray
        The molar susceptibility of the measurement with a fixed center.
    """
    
    def __init__(self, 
                 sample_filename : str | None = None,
                 background_filename : str | None = None,
                 direct_mapping : bool = True
        ) -> None:
        
        self.__set_sample_rdf__(sample_filename)
        self.__set_background_rdf__(background_filename)
        self.__create_measurement_datapoints__(direct_mapping)
        
    def __set_sample_rdf__(self, sample_filename : str) -> None:
        '''
        Sets the sample raw datafile.

        Parameters
        ----------
        sample_filename : str
            The filename of the raw datafile of the sample.

        Returns
        -------
        None.

        '''
        if sample_filename is not None:
            self.sample_rdf : RawDataFile | None = RawDataFile(sample_filename)
            self.name : str = sample_filename.split("/")[-1]
        else:
            self.sample_rdf : RawDataFile | None = None
            self.name : str = ''
            
    def __set_background_rdf__(self, background_filename : str) -> None:
        '''
        Sets the background raw datafile.

        Parameters
        ----------
        background_filename : str
            THe filename of the raw datafile of the background.

        Returns
        -------
        None.

        '''
        if background_filename is not None:
            self.background_rdf : RawDataFile | None = RawDataFile(background_filename)
        else:
            self.background_rdf : RawDataFile | None = None
        
    def __create_measurement_datapoints__(self, direct_mapping : bool) -> None:
        '''
        Creates all measurement datapoints according to the mapping option.

        Parameters
        ----------
        direct_mapping : bool
            If the mapping of the sample raw datapoints towards the background raw
            datapoints is direct or indirect.

        Raises
        ------
        err
            If a measurement datapoint can't be created.

        Returns
        -------
        None.

        '''
        self.datapoints : MeasurementDataPointContainer = MeasurementDataPointContainer()
        self.nr_not_matching_datapoints : int = 0
        if direct_mapping:
            if (self.sample_rdf is not None) and (self.background_rdf is not None):
                for s, b in zip(self.sample_rdf, self.background_rdf):
                    try:
                        if abs(s.temperature - b.temperature) > 0.25 or abs(s.field - b.field) > 2:
                            print(abs(s.temperature - b.temperature), abs(s.field - b.field))
                            self.nr_not_matching_datapoints += 1
                        else:
                            self.datapoints.add(s, b)
                    except ValueError as err:
                        print(s.raw_voltage)
                        print(b.raw_voltage)
                        print(s.temperature)
                        raise err
            elif self.sample_rdf is not None:
                for s in self.sample_rdf:
                    self.datapoints.add(s, None)
            else:
                for b in self.background_rdf:
                    self.datapoints.add(None, b)
        else:
            if (self.sample_rdf is not None) and (self.background_rdf is not None):
                max_temp_diff = 0.1
                max_field_diff = 10
                for s in self.sample_rdf:
                    bg = None
                    for b in self.background_rdf:
                        if abs(b.temperature - s.temperature) < max_temp_diff and abs(b.field - s.field) < max_field_diff and b.scan_direction == s.scan_direction:
                            if bg is None:
                                bg = b
                            else:
                                diff_1 = abs(bg.temperature - s.temperature) / s.temperature
                                diff_2 = abs(bg.field - s.field) / s.field if abs(s.field) > 1 else abs(bg.field - s.field)
                                sum_1 = diff_1 + diff_2
                                diff_1 = abs(b.temperature - s.temperature) / s.temperature
                                diff_2 = abs(b.field - s.field) / s.field if abs(s.field) > 1 else abs(b.field - s.field)
                                sum_2 = diff_1 + diff_2
                                if sum_2 < sum_1:
                                    bg = b
                    if bg is None:
                        print(s.temperature, s.field)
                        self.nr_not_matching_datapoints += 1
                    else:
                        self.datapoints.add(s, bg)
            else:
                for s in self.sample_rdf:
                    self.datapoints.add(s, None)
                    
    def datapoint_subset(self, index_map : np.ndarray) -> list[MeasurementDataPoint]:
        '''
        According to the index_map, all measurement datapoints at the given indices in the container
        will be returned.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be returned.

        Returns
        -------
        list[MeasurementDataPoint]
            The list of measurement datapoints of the given indices.

        '''
        datapoint_subset : list[MeasurementDataPoint] = []
        for index in index_map:
            datapoint_subset.append(self.datapoints[index])
        return datapoint_subset
        
    @property        
    def temperature(self) -> np.ndarray:
        '''
        Gets the temperatures of the measurement.

        Returns
        -------
        temperatures : np.ndarray
            The temperatures of the measurement.

        '''
        temperatures : np.ndarray = np.zeros(len(self.datapoints))
        for index, dp in enumerate(self.datapoints):
            temperatures[index] : float = dp.sample_rdp.temperature
        return temperatures
    
    def temperature_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the temperatures of the subset measurement.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        temperatures : np.ndarray
            The temperatures of the subset measurement.

        '''
        temperatures : np.ndarray = np.zeros(len(index_map))
        for index, index_dp in enumerate(index_map):
            temperatures[index] : float = self.datapoints[index_dp].sample_rdp.temperature
        return temperatures
    
    @property
    def field(self) -> np.ndarray:
        '''
        Gets the fields of the measurement.

        Returns
        -------
        fields : np.ndarray
            The fields of the measurement.

        '''
        fields : np.ndarray = np.zeros(len(self.datapoints))
        for index, dp in enumerate(self.datapoints):
            fields[index] : float = dp.sample_rdp.field
        return fields
    
    def field_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the fields of the subset measurement.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        fields : np.ndarray
            The fields of the subset measurement.

        '''
        fields : np.ndarray = np.zeros(len(index_map))
        for index, index_dp in enumerate(index_map):
            fields[index] : float = self.datapoints[index_dp].sample_rdp.field
        return fields
            
    @property        
    def moment(self) -> np.ndarray:
        '''
        Gets the moments of the measurement.

        Returns
        -------
        moments : np.ndarray
            The moments of the measurement.

        '''
        moments : np.ndarray = np.zeros(len(self.datapoints))
        for index, dp in enumerate(self.datapoints):
            moments[index] : float = dp.datapoint_result["moment"]
        return moments
    
    def moment_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the moments of the subset measurement.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        moments : np.ndarray
            The moments of the subset measurement.

        '''
        moments : np.ndarray = np.zeros(len(index_map))
        for index, index_dp in enumerate(index_map):
            moments[index] : float = self.datapoints[index_dp].datapoint_result["moment"]
        return moments
    
    @property        
    def volume_susceptibility(self) -> np.ndarray:
        '''
        Gets the volume susceptibility of the measurement.

        Returns
        -------
        volume_susceptibility : np.ndarray
            The volume susceptibility of the measurement.

        '''
        volume = float(self.sample_rdf.sample_mass) / (1000 * float(self.sample_rdf.sample_density))
        return self.moment / (volume * self.field)
    
    def volume_susceptibility_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the volume susceptibility of the subset measurement.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        volume_susceptibility_subset : np.ndarray
            The volume susceptibility of the subset measurement.

        '''
        volume = float(self.sample_rdf.sample_mass) / (1000 * float(self.sample_rdf.sample_density))
        return self.moment_subset(index_map) / (volume * self.field_subset(index_map))
    
    @property        
    def mass_susceptibility(self) -> np.ndarray:
        '''
        Gets the mass susceptibility of the measurement.

        Returns
        -------
        mass_susceptibility : np.ndarray
            The mass susceptibility of the measurement.

        '''
        return 1000 * self.moment / (float(self.sample_rdf.sample_mass) * self.field)
    
    def mass_susceptibility_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the mass susceptibility of the subset measurement.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        mass_susceptibility_subset : np.ndarray
            The mass susceptibility of the subset measurement.

        '''
        return 1000 * self.moment_subset(index_map) / (float(self.sample_rdf.sample_mass) * self.field_subset(index_map))
    
    @property        
    def molar_susceptibility(self) -> np.ndarray:
        '''
        Gets the molar susceptibility of the measurement.

        Returns
        -------
        molar_susceptibility : np.ndarray
            The molar susceptibility of the measurement.

        '''
        return float(self.sample_rdf.sample_molar_mass) * self.mass_susceptibility
    
    def molar_susceptibility_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the molar susceptibility of the subset measurement.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        molar_susceptibility_subset : np.ndarray
            The molar susceptibility of the subset measurement.

        '''
        return float(self.sample_rdf.sample_molar_mass) * self.mass_susceptibility_subset(index_map)
    
    @property        
    def moment_fixed_ctr(self) -> np.ndarray:
        '''
        Gets the moments of the measurement with a fixed center.

        Returns
        -------
        moments : np.ndarray
            The moments of the measurement with a fixed center.

        '''
        moments : np.ndarray = np.zeros(len(self.datapoints))
        for index, dp in enumerate(self.datapoints):
            moments[index] : float = dp.datapoint_result["moment_fixed_ctr"]
        return moments
    
    def moment_fixed_ctr_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the moments of the subset measurement with a fixed center.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        moments : np.ndarray
            The moments of the subset measurement with a fixed center.

        '''
        moments : np.ndarray = np.zeros(len(index_map))
        for index, index_dp in enumerate(index_map):
            moments[index] : float = self.datapoints[index_dp].datapoint_result["moment_fixed_ctr"]
        return moments
    
    @property        
    def volume_susceptibility_fixed_ctr(self) -> np.ndarray:
        '''
        Gets the volume susceptibility of the measurement with a fixed center.

        Returns
        -------
        volume_susceptibility : np.ndarray
            The volume susceptibility of the measurement with a fixed center.

        '''
        volume = float(self.sample_rdf.sample_mass) / (1000 * float(self.sample_rdf.sample_density))
        return self.moment_fixed_ctr / (volume * self.field)
    
    def volume_susceptibility_fixed_ctr_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the volume susceptibility of the subset measurement with a fixed center.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        volume_susceptibility_subset : np.ndarray
            The volume susceptibility of the subset measurement with a fixed center.

        '''
        volume = float(self.sample_rdf.sample_mass) / (1000 * float(self.sample_rdf.sample_density))
        return self.moment_fixed_ctr_subset(index_map) / (volume * self.field_subset(index_map))
    
    @property        
    def mass_susceptibility_fixed_ctr(self) -> np.ndarray:
        '''
        Gets the mass susceptibility of the measurement with a fixed center.

        Returns
        -------
        mass_susceptibility : np.ndarray
            The mass susceptibility of the measurement with a fixed center.

        '''
        return 1000 * self.moment_fixed_ctr / (float(self.sample_rdf.sample_mass) * self.field)
    
    def mass_susceptibility_fixed_ctr_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the mass susceptibility of the subset measurement with a fixed center.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        mass_susceptibility_subset : np.ndarray
            The mass susceptibility of the subset measurement with a fixed center.

        '''
        return 1000 * self.moment_fixed_ctr_subset(index_map) / (float(self.sample_rdf.sample_mass) * self.field_subset(index_map))
    
    @property        
    def molar_susceptibility_fixed_ctr(self) -> np.ndarray:
        '''
        Gets the molar susceptibility of the measurement with a fixed center.

        Returns
        -------
        molar_susceptibility : np.ndarray
            The molar susceptibility of the measurement with a fixed center.

        '''
        return float(self.sample_rdf.sample_molar_mass) * self.mass_susceptibility_fixed_ctr
    
    def molar_susceptibility_fixed_ctr_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the molar susceptibility of the subset measurement with a fixed center.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        molar_susceptibility_subset : np.ndarray
            The molar susceptibility of the subset measurement with a fixed center.

        '''
        return float(self.sample_rdf.sample_molar_mass) * self.mass_susceptibility_fixed_ctr_subset(index_map)
    
    @property
    def timestamp(self) -> np.ndarray:
        '''
        Gets the timestamps of the measurement.

        Returns
        -------
        moments : np.ndarray
            The timestamps of the measurement.

        '''
        timestamps : np.ndarray = np.zeros(len(self.datapoints))
        for index, dp in enumerate(self.datapoints):
            timestamps[index] : float = dp.sample_rdp.timestamp[-1]
        return timestamps
    
    def timestamp_subset(self, index_map : np.ndarray) -> np.ndarray:
        '''
        Gets the timestamps of the subset measurement.

        Parameters
        ----------
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.

        Returns
        -------
        timestamps : np.ndarray
            The timestamps of the subset measurement.

        '''
        timestamps : np.ndarray = np.zeros(len(index_map))
        for index, index_dp in enumerate(index_map):
            timestamps[index] : float = self.datapoints[index_dp].sample_rdp.timestamp[-1]
        return timestamps
    
    @property
    def nr_jump_corrected_datapoints(self) -> int:
        '''
        Gets the number of points, for which a correction of the voltage was necessary due
        to a jump in the signal.

        Returns
        -------
        nr_jump_corrected_datapoints : int
            The number of points, for which a correction was neccessary.

        '''
        i : int = 0
        for dp in self.datapoints:
            if dp.sample_rdp.jump_corrected:
                i += 1
            if dp.background_rdp is not None and dp.background_rdp.jump_corrected:
                i += 1
        return i
    
    def get_closest_datapoint(self,
                              goal_temp : float,
                              goal_moment : float,
                              return_index : bool = False) -> MeasurementDataPoint | int:
        '''
        Gets the closest datapoint to the given pair of temperature and field.

        Parameters
        ----------
        goal_temp : float
            The temperature which should be reached.
        goal_moment : float
            The moment which should be reached.
        return_index : bool, optional
            If the index is also returned. The default is False.

        Returns
        -------
        closest_datapoint : MeasurementDataPoint 
            The closest datapoint to the given tuple.
        
        or
        
        closest_datapoint : MeasurementDataPoint, index : int
            The closest datapoint to the given tuple and the corresponding index.
        

        '''
        temp = self.temperature
        temp_diff = ((temp - goal_temp) / (np.max(temp) - np.min(temp)))**2
        moment = self.moment
        moment_diff = ((moment - goal_moment) / (np.max(moment) - np.min(moment)))**2
        if return_index:
            return np.argmin(np.sqrt(temp_diff + moment_diff))
        else:
            return self.datapoints[np.argmin(np.sqrt(temp_diff + moment_diff))]
        
    def get_closest_datapoint_subset(self,
                                     goal_x : float,
                                     goal_moment : float,
                                     index_map : np.ndarray,
                                     temperature_dependent : bool = True,
                                     magnetisation_mode : str = "moment", 
                                     center_mode : str = "free",
                                     inverse : bool = False,
                                     return_index : bool = False) -> MeasurementDataPoint | int:
        '''
        Gets the closest datapoint in the subset to the given pair of temperature and field.

        Parameters
        ----------
        goal_x : float
            The temperature or field which should be reached.
        goal_moment : float
            The moment which should be reached.
        index_map : np.ndarray
            A list of indices, which measurement datapoints should be considered.
        temperature_dependent : bool, optional
            If the x coordinate is temperature or field. The default is True.
        magnetisation_mode : str, optional
            In what mode the magnetic moment is displayed. The default is "moment".
        center_mode : str, optional
            If the center is free or fixed. The default is "free".
        inverse : bool, optional
            If the given field is the inverse field. The default is False.
        return_index : bool, optional
            If the index is also returned. The default is False.

        Returns
        -------
        TYPE
            DESCRIPTION.

        '''
        if temperature_dependent:
            x_comp = self.temperature_subset(index_map)
        else:
            x_comp = self.field_subset(index_map)
        x_diff = ((x_comp - goal_x) / (np.max(x_comp) - np.min(x_comp)))**2
        
        if magnetisation_mode == "moment":
            if center_mode == "free":
                M_comp = self.moment_subset(index_map)
            elif center_mode == "fixed":
                M_comp = self.moment_fixed_ctr_subset(index_map)
        elif magnetisation_mode == "moment mu bohr":
            if center_mode == "free":
                M_comp = self.moment_subset(index_map)
            elif center_mode == "fixed":
                M_comp = self.moment_fixed_ctr_subset(index_map)
            M_comp = 1000 * M_comp * float(self.sample_rdf.sample_molar_mass) / (float(self.sample_rdf.sample_mass) * 5585)
        elif magnetisation_mode == "mass magnetisation":
            if center_mode == "free":
                M_comp = self.moment_subset(index_map)
            elif center_mode == "fixed":
                M_comp = self.moment_fixed_ctr_subset(index_map)
            M_comp = 1000 * M_comp / float(self.sample_rdf.sample_mass)
        elif magnetisation_mode == "molar magnetisation":
            if center_mode == "free":
                M_comp = self.moment_subset(index_map)
            elif center_mode == "fixed":
                M_comp = self.moment_fixed_ctr_subset(index_map)
            M_comp = M_comp / (float(self.sample_rdf.sample_mass) / (1000 * float(self.sample_rdf.sample_molar_mass)))
        elif magnetisation_mode == "volume":
            if center_mode == "free":
                M_comp = self.volume_susceptibility_subset(index_map)
            elif center_mode == "fixed":
                M_comp = self.volume_susceptibility_fixed_ctr_subset(index_map)
        elif magnetisation_mode == "mass":
            if center_mode == "free":
                M_comp = self.mass_susceptibility_subset(index_map)
            elif center_mode == "fixed":
                M_comp = self.mass_susceptibility_fixed_ctr_subset(index_map)
        elif magnetisation_mode == "molar":
            if center_mode == "free":
                M_comp = self.molar_susceptibility_subset(index_map)
            elif center_mode == "fixed":
                M_comp = self.molar_susceptibility_fixed_ctr_subset(index_map)
        
        if inverse:
            M_comp = 1 / M_comp
            
        M_diff = ((M_comp - goal_moment) / (np.max(M_comp) - np.min(M_comp)))**2
        if return_index:
            return np.argmin(np.sqrt(x_diff + M_diff))
        else:
            return self.datapoint_subset(index_map)[np.argmin(np.sqrt(x_diff + M_diff))]
    
    def get_closest_bg_datapoint(self, temp : float, field : float) -> RawDataPoint:
        '''
        Gets the closest datapoint to the given temperature and field.

        Parameters
        ----------
        temp : float
            The temperature which should be reached.
        field : float
            The field which should be reached.

        Returns
        -------
        RawDataPoint
            The closest datapoint to the given tuple.

        '''
        temp_diff = []
        field_diff = []
        for rdp in self.background_rdf:
            temp_diff.append(abs(temp - rdp.temperature))
            field_diff.append(abs(field - rdp.field))
        temp_diff = np.array(temp_diff)
        temp_diff = (temp_diff - np.min(temp_diff)) / (np.max(temp_diff) - np.min(temp_diff))
        field_diff = np.array(field_diff)
        field_diff = (field_diff - np.min(field_diff)) / (np.max(field_diff) - np.min(field_diff))
        return self.background_rdf[np.argmin(temp_diff + field_diff)]
        
    
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
        return self.datapoints[index]
    
    def __len__(self) -> int:
        '''
        Returns the amount of raw datapoints inside the container.

        Returns
        -------
        int
            The amount of raw datapoints inside the container.

        '''
        return len(self.datapoints)