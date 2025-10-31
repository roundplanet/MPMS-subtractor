# -*- coding: utf-8 -*-
"""
Created on Fri May 23 10:36:50 2025

@author: kaisjuli
"""

import os
import numpy as np

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

class MultiplePlotScrollWidget(QWidget):
    
    def __init__(self, measurements, show_labels = True) -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/multiple_plot_scroll_widget.ui", self)
        self.measurements = measurements 
        
        if show_labels:
            self.__show_labels__()
        else:
            self.__hide_labels__()
            
        self.measurement_cb.currentIndexChanged.connect(self.__populate_borders__)
        self.__populate_measurement_cb__()
        
    def __populate_measurement_cb__(self):
        measurement_names = []
        for measurement in self.measurements:
            measurement_names.append(measurement.sample_rdf.filename.split("/")[-1])
        if len(measurement_names) > 0:
            self.measurement_cb.insertItems(0, measurement_names)
            
    def __populate_borders__(self):
        measurement = self.measurements[self.measurement_cb.currentIndex()]
        T = measurement.temperature
        H = measurement.field
        self.T_min_sb.setRange(np.min(T)-0.01, np.max(T)+0.01)
        self.T_min_sb.setValue(np.min(T)-0.01)
        self.T_max_sb.setRange(np.min(T)-0.01, np.max(T)+0.01)
        self.T_max_sb.setValue(np.max(T)+0.01)
        self.H_min_sb.setRange(np.min(H)-0.01, np.max(H)+0.01)
        self.H_min_sb.setValue(np.min(H)-0.01)
        self.H_max_sb.setRange(np.min(H)-0.01, np.max(H)+0.01)
        self.H_max_sb.setValue(np.max(H)+0.01)
        
    def __show_labels__(self):
        self.measurement_frame.show()
        self.T_min_frame.show()
        self.T_max_frame.show()
        self.H_min_frame.show()
        self.H_max_frame.show()
        self.label_frame.show()
        self.delete_frame.show()
        
    def __hide_labels__(self):
        self.measurement_frame.hide()
        self.T_min_frame.hide()
        self.T_max_frame.hide()
        self.H_min_frame.hide()
        self.H_max_frame.hide()
        self.label_frame.hide()
        self.delete_frame.hide()
        
        