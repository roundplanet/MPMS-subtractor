# -*- coding: utf-8 -*-
"""
Created on Thu Aug 21 17:42:18 2025

@author: kaisjuli
"""
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog

from ..constants import COIL_RADIUS, COIL_DISTANCE, SYSTEM_CALIBRATION, DC_CALIBRATION_FACTOR

class ConstantsDialog(QDialog):
    '''
    A subclass of QDialog to show the defined constants in the constant file.
    
    Parameters
    ----------
        
    Attributes
    ----------
    coil_radius_sb : QDoubleSpinBox
        The spinbox which shows the value of the coil radius.
    coil_distance_sb : QDoubleSpinBox
        The spinbox which shows the value of the distance between the coils.
    system_calibration_sb : QDoubleSpinBox
        The spinbox which shows the value of the system calibration factor.
    dc_calibration_factor_sb : QDoubleSpinBox
        The spinbox which shows the value of the DC calibration factor.
    
    '''
    
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/constants_dialog.ui", self)
        
        self.coil_radius_sb.setValue(COIL_RADIUS)
        self.coil_distance_sb.setValue(COIL_DISTANCE)
        self.system_calibration_sb.setValue(SYSTEM_CALIBRATION)
        self.dc_calibration_factor_sb.setValue(DC_CALIBRATION_FACTOR)
    