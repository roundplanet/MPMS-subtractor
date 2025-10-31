# -*- coding: utf-8 -*-
"""
Created on Wed May 14 16:06:45 2025

@author: kaisjuli
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..data import Measurement
    from ..data import MeasurementDataPoint
    from .measurementdataplot import MeasurementDataplot
    
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QMenu, QPushButton, QHBoxLayout
from PyQt5.QtGui import QCursor

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from ..calculation import gradiometer_function, subtract_background

class DatapointPlot(QDialog):
    
    def __init__(self, parent : MeasurementDataplot, measurement : Measurement, index : int):
        super().__init__()
        
        self.__init_widget__()
        self.parent : MeasurementDataplot = parent
        self.measurement : Measurement = measurement
        self.index : int = index
        self.datapoint : MeasurementDataPoint = self.measurement[index]
        self.plot_datapoint_data()
        
        self.figure_canvas.mpl_connect("pick_event", self.actionClick)
        self.figure_canvas.mpl_connect("button_press_event", self.actionClick2)
    
    def __init_widget__(self):
        self.figure = Figure()
        self.figure_canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.figure_canvas, self)
        
        layout = QVBoxLayout()
        layout_mpl = QVBoxLayout()
        layout_mpl.addWidget(self.toolbar)
        layout_mpl.addWidget(self.figure_canvas)
        layout.addLayout(layout_mpl)
        layout_buttons = QHBoxLayout()
        self.previous_button = QPushButton("previous")
        self.previous_button.clicked.connect(self.change_to_previous_datapoint)
        layout_buttons.addWidget(self.previous_button)
        self.next_button = QPushButton("next")
        self.next_button.clicked.connect(self.change_to_next_datapoint)
        layout_buttons.addWidget(self.next_button)
        layout.addLayout(layout_buttons)
        self.setLayout(layout)
        
        self.ax = self.figure.add_subplot(111)
        self.figure.tight_layout()
        #self.figure_canvas.draw()
        
    def plot_datapoint_data(self):
        self.parent.scatter_item_dp.remove()
        self.parent.scatter_item_dp = self.parent.ax.scatter(
            self.datapoint.sample_rdp.temperature,
            self.datapoint.datapoint_result["moment"], c="r"
        )
        self.parent.figure_canvas.draw()
        
        self.ax.cla()
        self.ax.scatter(self.datapoint.sample_rdp.raw_position, self.datapoint.sample_rdp.raw_voltage, picker=True, label="measurement")
        if self.datapoint.background_rdp is not None:
            self.ax.scatter(self.datapoint.background_rdp.raw_position, self.datapoint.background_rdp.raw_voltage, picker=True, label="background measurement")
            self.ax.scatter(*subtract_background(self.datapoint.sample_rdp, self.datapoint.background_rdp), picker=True, label="without background")
        self.ax.plot(self.datapoint.sample_rdp.raw_position, gradiometer_function(self.datapoint.sample_rdp.raw_position, *self.datapoint.datapoint_result["fit_coeff"]), picker=True, label="fit")
        self.figure.legend()
        self.figure_canvas.draw()
        
    def change_to_previous_datapoint(self, event):
        new_index = self.index - 1
        if new_index == self.parent.start_index:
            self.previous_button.setEnabled(False)
        elif new_index == self.parent.end_index - 2:
            self.next_button.setEnabled(True)
        self.change_datapoint(new_index)
        
    def change_to_next_datapoint(self, event):
        new_index = self.index + 1
        if new_index == self.parent.end_index - 1:
            self.next_button.setEnabled(False)
        elif new_index == self.parent.start_index + 1:
            self.previous_button.setEnabled(True)
        self.change_datapoint(new_index)
        
    def change_datapoint(self, new_index):
        self.index : int = new_index
        self.datapoint : MeasurementDataPoint = self.measurement[new_index]
        self.plot_datapoint_data()
        
    def actionClick(self, event):
        if event.mouseevent.dblclick:
            print(event.mouseevent.dblclick)
            print(event)
        
    def actionClick2(self, event):
        if event.button == 3:
            self.popMenu = QMenu(self)
            self.popMenu.addAction("test")
            #self.popMenu.addAction(noteAction_2)
        
            cursor = QCursor()
            self.popMenu.popup(cursor.pos())
            print(event)