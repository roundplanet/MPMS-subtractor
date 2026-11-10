# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 16:10:08 2026

@author: kaisjuli
"""

import numpy as np

from .mpmsrawdatapoint import MPMSRawDataPoint
from .rawdatapointcontainer import RawDataPointContainer

class MPMSRawDataFile():
    """
    A class to represent a raw datafile.
    
    Parameters
    ----------
    filename : str
        The filename of the raw datafile.
        
    Attributes
    ----------
    datapoints : RawDataPointContainer
        The container which stores all raw datapoints from the file.
    filename : str
        The filename of the raw datafile.
        
    appname : str
        The appname in the datafile.
    coil_serial_number : str
        The serial_number of the used coils.
    moment_units : str
        The used units for the moment.
    sample_material : str
        The material of the sample.
    sample_mass : str
        The mass of the sample.
    sample_volume : str
        The volume of the sample.
    sample_molecular_weight : str
        The molecular weight of the sample.
    sample_size : str
        The size of the sample.
    sample_shape : str
        The shape of the sample.
    sample_holder : str
        The used sample holder.
    sample_holder_detail : str
        Details to the used sample holder.
    sample_offset : str
        The offset in the scan to the sample.
    sample_density : str
        The density of the sample.
    sample_molar_mass : str
        The molar mass of the sample.
    """
    
    def __init__(self, filename : str) -> None:
        self.datapoints : RawDataPointContainer = RawDataPointContainer()
        self.filename : str = filename
        
        with open(filename) as file:
            info_buffer : list[str] = []
            for index, line in enumerate(file):
                if line[:5] == "TITLE":
                    self.title : str = line[6:-1]
                if line[:4] == "INFO":
                    info_buffer.append(line)
                if line == "[Data]\n":
                    break
            
        data_arr : np.array = np.loadtxt(filename, skiprows=index + 2, delimiter=",", usecols=[0,2,3,4,7,9,12])
        splitted_arr = np.split(data_arr, np.where(data_arr[1:, 4]-data_arr[:-1, 4]<0)[0]+1)
        diag_arr : np.array = np.loadtxt(filename[:-3] + "diag", skiprows=27, delimiter=",", usecols=[7,8])
        
        for index, arr in enumerate(splitted_arr):
            info_dic = {}
            info_dic["RANGE"] : int = int(diag_arr[index, 0])
            info_dic["GAIN"] : int = int(diag_arr[index, 1])
            self.datapoints.add(info_dic, arr, "MPMS")
        self.__convert_info_buffer__(info_buffer)
            
    def __convert_info_buffer__(self, info_buffer : list[str]) -> None:
        '''
        Extracts all information from the info buffer.

        Parameters
        ----------
        info_buffer : list[str]
            Contains all information from the header of the raw datafile.

        Returns
        -------
        None.

        '''
        def get_info_element(info_list : list[str], key : str) -> str | None:
            '''
            Gets the information about the specific key.

            Parameters
            ----------
            info_list : list[str]
                A list of encoded secundary information about the datapoint.
            key : str
                The key to be search after.

            Returns
            -------
            float
                The specific information from the key.

            '''
            result : str = [sub for sub in info_list if key in sub]
            if len(result) == 0:
                return None
            return ",".join(result[0].split(",")[2:-1])
        
        self.appname : str = get_info_element(info_buffer, "APPNAME")
        self.coil_serial_number : str = get_info_element(info_buffer, "COIL_SERIAL_NUMBER")
        self.moment_units : str = get_info_element(info_buffer, "MOMENT_UNITS")
        self.sample_material : str = get_info_element(info_buffer, "NAME")
        self.sample_comment : str = get_info_element(info_buffer, "COMMENT")
        self.sample_mass : str = get_info_element(info_buffer, "WEIGHT")
        self.sample_volume : str = get_info_element(info_buffer, "SAMPLE_VOLUME")
        self.sample_molecular_weight : str = get_info_element(info_buffer, "SAMPLE_MOLECULAR_WEIGHT")
        self.sample_size : str = get_info_element(info_buffer, "LENGTH")
        self.sample_shape : str = get_info_element(info_buffer, "SHAPE")
        self.sample_holder : str = get_info_element(info_buffer, "SAMPLE_HOLDER")
        self.sample_holder_detail : str = get_info_element(info_buffer, "SAMPLE_HOLDER_DETAIL")
        self.sample_offset : str = get_info_element(info_buffer, "SAMPLE_OFFSET")
        self.sample_density : float | None = get_info_element(info_buffer, "DENSITY")
        self.sample_molar_mass : float | None = get_info_element(info_buffer, "MOLAR_MASS")
        
    def print_sample_info(self) -> None:
        s : str = "Sample infos:\n"
        s += "material = {}\n".format(self.sample_material)
        s += "comment = {}\n".format(self.sample_comment)
        s += "mass = {}\n".format(self.sample_mass)
        s += "volume = {}\n".format(self.sample_volume)
        s += "molecular weight = {}\n".format(self.sample_molecular_weight)
        s += "size = {}\n".format(self.sample_size)
        s += "shape = {}\n".format(self.sample_shape)
        s += "holder = {}\n".format(self.sample_holder)
        s += "holder detail = {}\n".format(self.sample_holder_detail)
        s += "offset = {}\n".format(self.sample_offset)
        s += "density = {}\n".format(self.sample_density)
        s += "molar mass = {}\n".format(self.sample_molar_mass)
        print(s)
            
    def modify_line_in_file(self, search_text : str, replace_text : str) -> None:
        '''
        Modifies the line in a raw datafile which contains the search_text by the
        replace_text.

        Parameters
        ----------
        search_text : str
            The text to search for.
        replace_text : str
            The text to replace the searched text.

        Returns
        -------
        None.

        '''
        with open(self.filename, 'r') as file:
            lines : list[str] = file.readlines()
    
        modified = False
        for i, line in enumerate(lines):
            if search_text in line:
                lines[i] : str = replace_text
                modified : bool = True
                break
            if "[Data]" in line:
                break
    
        if not modified:
            for i, line in enumerate(lines):
                if "WEIGHT" in line:
                    lines[i] : str = line + replace_text
                    break
        with open(self.filename, 'w') as file:
            file.writelines(lines)
        
    def set_sample_density(self, new_sample_density : float) -> None:
        '''
        Sets the new sample density in the raw datafile.

        Parameters
        ----------
        new_sample_density : float
            The new sample density.

        Returns
        -------
        None.

        '''
        self.sample_density : float = new_sample_density
        self.modify_line_in_file("DENSITY", "INFO, DENSITY, {:.3f}\n".format(new_sample_density))
    
    def set_sample_molar_mass(self, new_sample_molar_mass : float) -> None:
        '''
        Sets the new sample molar mass in the raw datafile.

        Parameters
        ----------
        new_sample_molar_mass : float
            The new sample molar mass.

        Returns
        -------
        None.

        '''
        self.sample_molar_mass : float = new_sample_molar_mass
        self.modify_line_in_file("MOLAR_MASS", "INFO, MOLAR_MASS, {:.3f}\n".format(new_sample_molar_mass))
        
    def __getitem__(self, index : int) -> MPMSRawDataPoint:
        '''
        Gets the datapoint from the container at the desired position.

        Parameters
        ----------
        index : int
            The desired position in the container.

        Returns
        -------
        MPMS3RawDataPoint
            The raw datapoint at the specified position.

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