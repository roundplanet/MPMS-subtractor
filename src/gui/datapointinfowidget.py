# -*- coding: utf-8 -*-
"""
Created on Fri May 30 14:33:53 2025

@author: kaisjuli
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .measurementdatapoint import MeasurementDataPoint
    from .datapointplotdialog import DatapointPlotDialog
    
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5 import QtCore

class DatapointInfoWidget(QWidget):
    '''
    A class to represent a measurement and provide methods to access the fitted data.
    
    Parameters
    ----------
    parent : DatapointPlotDialog
        The Dialog on which the widget should appear.
        
    Attributes
    ----------
    toolButton : QToolButton
        The button which closes the widget.
    datapoint_nr_lb : QLabel
        The label which shows the number of the datapoint in the measurement.
    low_temp_lb : QLabel
        The label which shows the lower temperature of the sample datapoint.
    low_temp_2_lb : QLabel
        The label which shows the lower temperature of the background datapoint.
    high_temp_lb : QLabel
        The label which shows the higher temperature of the sample datapoint.
    high_temp_2_lb : QLabel
        The label which shows the higher temperature of the background datapoint.
    avg_temp_lb : QLabel
        The label which shows the average temperature of the sample datapoint.
    avg_temp_2_lb : QLabel
        The label which shows the average temperature of the background datapoint.
    low_field_lb : QLabel
        The label which shows the lower field of the sample datapoint.
    low_field_2_lb : QLabel
        The label which shows the lower field of the background datapoint.
    high_field_lb : QLabel
        The label which shows the higher field of the sample datapoint.
    high_field_2_lb : QLabel
        The label which shows the higher field of the background datapoint.
    drift_lb : QLabel
        The label which shows the drift of the sample datapoint
    drift_2_lb : QLabel
        The label which shows the drift of the background datapoint
    slope_lb : QLabel
        The label which shows the slope of the sample datapoint
    slope_2_lb : QLabel
        The label which shows the slope of the background datapoint
    squid_range_lb : QLabel
        The label which shows the squid range of the sample datapoint
    squid_range_2_lb : QLabel
        The label which shows the squid range of the background datapoint
    given_center_lb : QLabel
        The label which shows the given center of the sample datapoint
    given_center_2_lb : QLabel
        The label which shows the given center of the background datapoint
    calculated_center_lb : QLabel
        The label which shows the calculated center of the sample datapoint
    calculated_center_2_lb : QLabel
        The label which shows the calculated center of the background datapoint
    amplitude_fixed_lb : QLabel
        The label which shows the amplitude with fixed center of the sample datapoint
    amplitude_fixed_2_lb : QLabel
        The label which shows the amplitude with fixed center of the background datapoint
    amplitude_free_lb : QLabel
        The label which shows the amplitude with free center of the sample datapoint
    amplitude_free_2_lb : QLabel
        The label which shows the amplitude with free center of the background datapoint
    amplitude_sample_lb : QLabel
        The label which shows the fitted amplitude of the sample datapoint
    amplitude_bg_lb : QLabel
        The label which shows the fitted amplitude of the background datapoint
    drift_sample_lb : QLabel
        The label which shows the fitted drift of the sample datapoint
    drift_bg_lb : QLabel
        The label which shows the fitted drift of the background datapoint
    y_offset_sample_lb : QLabel
        The label which shows the fitted y-offset of the sample datapoint
    y_offset_bg_lb : QLabel
        The label which shows the fitted y-offset of the background datapoint
    x_offset_sample_lb : QLabel
        The label which shows the fitted x-offset of the sample datapoint
    x_offset_bg_lb : QLabel
        The label which shows the fitted x-offset of the background datapoint
    sample_jump_corr_lb : QLabel
        The label which shows if the sample datapoint had a jump correction.
    background_jump_corr_lb : QLabel
        The label which shows if the background datapoint had a jump correction.
    scan_direction_lb : QLabel
        The label which shows the scan direction of the sample datapoint
    scan_direction_2_lb : QLabel
        The label which shows the scan direction of the background datapoint
    
    '''
    
    
    def __init__(self, parent : DatapointPlotDialog) -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/datapoint_info_widget.ui", self)
        
        self.setParent(parent)
        self.toolButton.setText("\u2A09")
        self.toolButton.clicked.connect(self.hide)
        self.raw_file_info_lb.setText("<i>raw file infos:</i>")
        self.fitted_info_lb.setText("<i>fitted infos:</i>")
        self.other_info_lb.setText("<i>other:</i>")
    
    def display_infos(self, measurment_dp : MeasurementDataPoint, index : int) -> None:
        '''
        Updates the corresponding information about the datapoint.

        Parameters
        ----------
        measurment_dp : MeasurementDataPoint
            The measurement datapoint which information should be shown.
        index : int
            The number of the datapoint in the measurement.

        Returns
        -------
        None.

        '''
        
        def formatter(num):
            if abs(num) > 1e-1:
                return str(round(num, 2))
            return f"{num:.2e}"
        
        self.datapoint_nr_lb.setText("Datapoint #{}".format(index))
        self.low_temp_lb.setText(str(round(measurment_dp.sample_rdp.low_temp, 2)) + " K")
        self.high_temp_lb.setText(str(round(measurment_dp.sample_rdp.high_temp, 2)) + " K")
        self.avg_temp_lb.setText(str(round(measurment_dp.sample_rdp.avg_temp, 2)) + " K")
        self.low_field_lb.setText(str(round(measurment_dp.sample_rdp.low_field, 2)) + " Oe")
        self.high_field_lb.setText(str(round(measurment_dp.sample_rdp.high_field, 2)) + " Oe")
        self.drift_lb.setText("{:.2e}".format(measurment_dp.sample_rdp.drift) + " V/s")
        self.slope_lb.setText("{:.2e}".format(measurment_dp.sample_rdp.slope) + " V/mm")
        self.squid_range_lb.setText(str(round(measurment_dp.sample_rdp.squid_range)))
        self.given_center_lb.setText(str(round(measurment_dp.sample_rdp.given_center, 2)) + " mm")
        self.calculated_center_lb.setText(str(round(measurment_dp.sample_rdp.calculated_center, 2)) + " mm")
        self.amplitude_fixed_lb.setText(str(round(measurment_dp.sample_rdp.amp_fixed, 3)) + " V")
        self.amplitude_free_lb.setText(str(round(measurment_dp.sample_rdp.amp_free, 3)) + " V")
        self.amplitude_sample_lb.setText(formatter(measurment_dp.sample_result["fit_coeff"][0]) + " V")
        self.drift_sample_lb.setText(formatter(measurment_dp.sample_result["fit_coeff"][2]) + " V/mm")
        self.y_offset_sample_lb.setText(formatter(measurment_dp.sample_result["fit_coeff"][1]) + " V")
        self.x_offset_sample_lb.setText(formatter(measurment_dp.sample_result["fit_coeff"][3]) + " mm")
        self.sample_jump_corr_lb.setText(str(measurment_dp.sample_rdp.jump_corrected))
        self.scan_direction_lb.setText(measurment_dp.sample_rdp.scan_direction)
        if measurment_dp.background_rdp is not None:
            self.low_temp_2_lb.setText(str(round(measurment_dp.background_rdp.low_temp, 2)) + " K")
            self.high_temp_2_lb.setText(str(round(measurment_dp.background_rdp.high_temp, 2)) + " K")
            self.avg_temp_2_lb.setText(str(round(measurment_dp.background_rdp.avg_temp, 2)) + " K")
            self.low_field_2_lb.setText(str(round(measurment_dp.background_rdp.low_field, 2)) + " Oe")
            self.high_field_2_lb.setText(str(round(measurment_dp.background_rdp.high_field, 2)) + " Oe")
            self.drift_2_lb.setText("{:.2e}".format(measurment_dp.background_rdp.drift) + " V/s")
            self.slope_2_lb.setText("{:.2e}".format(measurment_dp.background_rdp.slope) + " V/mm")
            self.squid_range_2_lb.setText(str(round(measurment_dp.background_rdp.squid_range)))
            self.given_center_2_lb.setText(str(round(measurment_dp.background_rdp.given_center, 2)) + " mm")
            self.calculated_center_2_lb.setText(str(round(measurment_dp.background_rdp.calculated_center, 2)) + " mm")
            self.amplitude_fixed_2_lb.setText(str(round(measurment_dp.background_rdp.amp_fixed, 3)) + " V")
            self.amplitude_free_2_lb.setText(str(round(measurment_dp.background_rdp.amp_free, 3)) + " V")
            self.amplitude_bg_lb.setText(formatter(measurment_dp.background_result["fit_coeff"][0]) + " V")
            self.drift_bg_lb.setText(formatter(measurment_dp.background_result["fit_coeff"][2]) + " V/mm")
            self.y_offset_bg_lb.setText(formatter(measurment_dp.background_result["fit_coeff"][1]) + " V")
            self.x_offset_bg_lb.setText(formatter(measurment_dp.background_result["fit_coeff"][3]) + " mm")
            self.background_jump_corr_lb.setText(str(measurment_dp.background_rdp.jump_corrected))
            self.scan_direction_2_lb.setText(measurment_dp.background_rdp.scan_direction)
        return
    
    def show_widget(self, position : list[float]) -> None:
        '''
        Shows the widget at the corresponding position with the right upper corner.

        Parameters
        ----------
        position : list[float]
            Coordinates of the click from the user.

        Returns
        -------
        None.

        '''
        self.show()
        self.adjustSize()
        self.move(position[0] - self.width(), position[1] + 10)