# -*- coding: utf-8 -*-
"""
Created on Tue May 20 10:54:06 2025

@author: kaisjuli
"""
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QRadioButton, QButtonGroup

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class OpenPlotDialog(QDialog):
    
    def __init__(self, measurement_container) -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/open_plot_dialog.ui", self)
        self.setModal(False)

        self.measurement_container = measurement_container
        self.figure = Figure()
        self.figure_canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.figure.tight_layout()
        self.verticalLayout.addWidget(self.figure_canvas)
        
        self.radiobuttons = QButtonGroup()
        self.radiobuttons.setExclusive(True)
        self.radiobuttons.buttonClicked.connect(self.__handle_rb_click__)
        self.__fill_from_container__()
        self.index_start_sb.valueChanged.connect(self.__update_borders__)
        self.index_end_sb.valueChanged.connect(self.__update_borders__)
        self.index_start_sb.setEnabled(False)
        self.index_end_sb.setEnabled(False)
        
        self.temperatures = None
        self.fields = None
        self.timestamps = None
        self.moments = None
        self.measurement = None
        
    def __fill_from_container__(self):
        for measurement in self.measurement_container:
            rb = QRadioButton(measurement.sample_rdf.filename.split("/")[-1])
            self.radiobuttons.addButton(rb)
            self.scrollArea_vl.addWidget(rb)
            
    def __handle_rb_click__(self, event):
        self.measurement = self.measurement_container.get_from_filename(event.text())
        self.index_end_sb.setValue(len(self.measurement) - 1)
        self.index_end_sb.setRange(1, len(self.measurement) - 1)
        self.index_start_sb.setRange(0, len(self.measurement) - 2)
        self.temperatures = self.measurement.temperature
        self.fields = self.measurement.field
        self.timestamps = self.measurement.timestamp
        self.moments = self.measurement.moment
        self.__update_borders__(None)
        self.index_start_sb.setEnabled(True)
        self.index_end_sb.setEnabled(True)
        
    def __update_borders__(self, event):
        start_index = self.index_start_sb.value()
        end_index = self.index_end_sb.value()
        self.index_end_sb.setMinimum(start_index + 1)
        self.index_start_sb.setMaximum(end_index - 1)
        if self.timestamps is not None:
            self.timestamp_start_lb.setText(str(round(self.timestamps[start_index], 2)))
            self.timestamp_end_lb.setText(str(round(self.timestamps[end_index], 2)))
            self.temperature_start_lb.setText(str(round(self.temperatures[start_index], 1)) + " K")
            self.temperature_end_lb.setText(str(round(self.temperatures[end_index], 1)) + " K")
            self.field_start_lb.setText(str(round(self.fields[start_index], 1)) + " Oe")
            self.field_end_lb.setText(str(round(self.fields[end_index], 1)) + " Oe")
            self.ax.cla()
            self.ax.scatter(self.temperatures[start_index:end_index+1], self.moments[start_index:end_index+1])
            self.figure_canvas.draw()
