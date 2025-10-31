# -*- coding: utf-8 -*-
"""
Created on Wed May 14 08:28:34 2025

@author: kaisjuli
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .rawdatapoint import RawDataPoint
    
import numpy as np
    
from ..calculation import subtract_background, fit_signal, convert_amplitude_to_moment
    
class MeasurementDataPoint():
    """
    A class to represent a measurement datapoint, containing of a sample raw datapoint and
    if given a background raw datapoint.
    All result dictionaries contain
        - p0 : start conditions
        - moment : calculated magnetic moment with a free center
        - moment_err : error of the calculated magnetic moment with a free center
        - fit_coeff : coefficients of the fit with a free center
        - fit_err : error of the coefficients of the fit with a free center
        - fixed_ctr : The value of the fixed center.
        - moment_fixed_ctr : calculated magnetic moment with a fixed center
        - moment_fixed_ctr_err : error of the calculated magnetic moment with a fixed center
        - fit_fixed_ctr_coeff : coefficients of the fit with a fixed center
        - fit_fixed_ctr_err : error of the coefficients of the fit with a fixed center
    
    Parameters
    ----------
    sample_rdp : RawDataPoint | None
        The raw datapoint of the sample. The default is None.
    background_rdp : RawDataPoint | None
        The raw datapoint of the background. The default is None.
        
    Attributes
    ----------
    sample_rdp : RawDataPoint | None
        The raw datapoint of the sample. The default is None.
    background_rdp : RawDataPoint | None
        The raw datapoint of the background. The default is None.
    fitting_was_possible : bool
        States if the fitting was possible.
        
    sample_result : dict[str, None | float | list[float] | np.ndarray]
        The result of the fitting procedure of the sample raw datafile.
    background_result : dict[str, None | float | list[float] | np.ndarray]
        The result of the fitting procedure of the background raw datafile.
    datapoint_result : dict[str, None | float | list[float] | np.ndarray]
        The result of the fitting procedure of the measurement datapoint.
    """
    
    def __init__(self, 
                 sample_rdp : RawDataPoint | None = None,
                 background_rdp : RawDataPoint | None = None
        ) -> None:
        
        self.sample_rdp : RawDataPoint | None = sample_rdp
        self.background_rdp : RawDataPoint | None = background_rdp
        self.fitting_was_possible : bool = True
        
        # TODO: check for compatibility 
        
        self.sample_result : dict[str, None | float | list[float] | np.ndarray] = {
            "p0" : None,
            "moment" : None,
            "moment_err" : None,
            "fit_coeff" : None,
            "fit_err" : None,
            "fixed_ctr" : None,
            "moment_fixed_ctr" : None,
            "moment_fixed_ctr_err" : None,
            "fit_fixed_ctr_coeff" : None,
            "fit_fixed_ctr_err" : None,
            }
        self.background_result : dict[str, None | float | list[float] | np.ndarray] = {
            "p0" : None,
            "moment" : None,
            "moment_err" : None,
            "fit_coeff" : None,
            "fit_err" : None,
            "fixed_ctr" : None,
            "moment_fixed_ctr" : None,
            "moment_fixed_ctr_err" : None,
            "fit_fixed_ctr_coeff" : None,
            "fit_fixed_ctr_err" : None,
            }
        self.datapoint_result : dict[str, None | float | list[float] | np.ndarray] = {
            "p0" : None,
            "moment" : None,
            "moment_err" : None,
            "fit_coeff" : None,
            "fit_err" : None,
            "fixed_ctr" : None,
            "moment_fixed_ctr" : None,
            "moment_fixed_ctr_err" : None,
            "fit_fixed_ctr_coeff" : None,
            "fit_fixed_ctr_err" : None,
            }
        
        self.__calculate_moments__()
        
    def __calculate_moments__(self):
        '''
        Calculates the moments of the sample and datapoint and, if given, from the 
        background as well.

        Returns
        -------
        None.

        '''
        def perform_fitting(pos : np.ndarray,
                            voltage : np.ndarray,
                            fixed_ctr : float,
                            save_dict : dict) -> None:
            '''
            Performes the fitting on the position and voltage data given with a fixed center
            and saves the result in the corresponding dictionary.

            Parameters
            ----------
            pos : np.ndarray
                The positions of the signal.
            voltage : np.ndarray
                The voltages of the signal.
            fixed_ctr : float
                The value of the fixed center.
            save_dict : dict
                The dictionary, in which all results have to be saved.

            Returns
            -------
            None.

            '''
            save_dict["fixed_ctr"] : float = fixed_ctr
            save_dict["p0"] : list[float] = [0, np.mean(voltage), 0, fixed_ctr]
            #try:
            res : list[np.ndarray] = fit_signal(pos, voltage, save_dict["p0"])
            save_dict["moment"] : float = convert_amplitude_to_moment(res[0][0])
            save_dict["moment_err"] : float = abs(convert_amplitude_to_moment(np.sqrt(np.diag(res[1]))[0]))
            save_dict["fit_coeff"] : np.ndarray = res[0]
            save_dict["fit_err"] : np.ndarray = res[1]
            #except RuntimeError:
            #    self.fitting_was_possible = False
            #try:
            res : list[np.ndarray] = fit_signal(pos, voltage, save_dict["p0"][:3], True, fixed_ctr)
            save_dict["moment_fixed_ctr"] : float = convert_amplitude_to_moment(res[0][0])
            save_dict["moment_fixed_ctr_err"] : float = abs(convert_amplitude_to_moment(np.sqrt(np.diag(res[1]))[0]))
            save_dict["fit_fixed_ctr_coeff"] : np.ndarray = res[0]
            save_dict["fit_fixed_ctr_err"] : np.ndarray = res[1]
            #except RuntimeError:
            #    self.fitting_was_possible = False
        
        if self.sample_rdp is not None:
            perform_fitting(
                self.sample_rdp.raw_position,
                self.sample_rdp.raw_voltage,
                self.sample_rdp.given_center,
                self.sample_result
            )
            if self.background_rdp is None:
                self.datapoint_result : dict = self.sample_result.copy()
        if self.background_rdp is not None:
            perform_fitting(
                self.background_rdp.raw_position,
                self.background_rdp.raw_voltage,
                self.background_rdp.given_center,
                self.background_result
            )
            if self.sample_rdp is None:
                self.datapoint_result : dict = self.background_result.copy()
        if self.sample_rdp is not None and self.background_rdp is not None:
            pos_wo_bg, voltage_wo_bg = subtract_background(self.sample_rdp, self.background_rdp)
            perform_fitting(
                pos_wo_bg,
                voltage_wo_bg,
                (self.background_rdp.given_center + self.sample_rdp.given_center) / 2, # TODO: einfügen dass einstellbar ist
                self.datapoint_result
            )
            
    def convert_to_volume_susceptibility(self,
                                         mass : str,
                                         density : str,
                                         free_center : bool = True) -> float:
        '''
        Converts the fitted moment to volume susceptibility.

        Parameters
        ----------
        mass : str
            The mass of the sample.
        density : str
            The density of the sample.
        free_center : bool, optional
            If the moment of the fit with the free center should be returned or with the
            fixed center. The default is True.

        Returns
        -------
        float
            The converted moment.

        '''
        volume = float(mass) / (1000 * float(density))
        if free_center:
            return self.datapoint_result["moment"] / (volume * self.sample_rdp.field)
        else:
            return self.datapoint_result["moment_fixed_ctr"] / (volume * self.sample_rdp.field)
    
    def convert_to_mass_susceptibility(self, mass : str, free_center : bool = True) -> float:
        '''
        Converts the fitted moment to mass susceptibility.

        Parameters
        ----------
        mass : str
            The mass of the sample.
        free_center : bool, optional
            If the moment of the fit with the free center should be returned or with the
            fixed center. The default is True.

        Returns
        -------
        float
            The converted moment.

        '''
        if free_center:
            return 1000 * self.datapoint_result["moment"] / (float(mass) * self.sample_rdp.field)
        else:
            return 1000 * self.datapoint_result["moment_fixed_ctr"] / (float(mass) * self.sample_rdp.field)

    def convert_to_molar_susceptibility(self,
                                        mass : str,
                                        molar_mass : str,
                                        free_center : bool = True):
        '''
        Converts the fitted moment to molar susceptibility.

        Parameters
        ----------
        mass : str
            The mass of the sample.
        molar_mass : str
            The molar mass of the sample.
        free_center : bool, optional
            If the moment of the fit with the free center should be returned or with the
            fixed center. The default is True.

        Returns
        -------
        float
            The converted moment.

        '''
        return float(molar_mass) * self.convert_to_mass_susceptibility(mass, free_center)