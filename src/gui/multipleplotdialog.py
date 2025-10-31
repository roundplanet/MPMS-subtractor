 # -*- coding: utf-8 -*-
"""
Created on Fri May 23 10:27:00 2025

@author: kaisjuli
"""

import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox
from PyQt5 import QtCore

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from .multipleplotscrollwidget import MultiplePlotScrollWidget

class MultiplePlotDialog(QDialog):
    
    def __init__(self, measurements) -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/multiple_plot_dialog.ui", self)
        self.measurements = measurements
        
        self.figure = Figure()
        self.figure.set_layout_engine("tight")
        self.figure_canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.verticalLayout.addWidget(self.figure_canvas)
        
        self.scroll_layout.setAlignment(QtCore.Qt.AlignTop)
        self.add_pb.clicked.connect(self.__add_new_scroll_widget__)
        self.update_pb.clicked.connect(self.__update_plot__)
        
    def __add_new_scroll_widget__(self, event):
        if len(self.scroll_layout) > 0:
            widget = MultiplePlotScrollWidget(self.measurements, show_labels=False)#
            widget.delete_pb.clicked.connect(lambda event: self.__delete_scroll_widget__(event, widget))
            self.scroll_layout.addWidget(widget)
        else:
            widget = MultiplePlotScrollWidget(self.measurements, show_labels=True)#self.window().measurements
            widget.delete_pb.clicked.connect(lambda event: self.__delete_scroll_widget__(event, widget))
            self.scroll_layout.addWidget(widget)
        
    def __delete_scroll_widget__(self, event, widget):
        for index in range(self.scroll_layout.count()):
            if widget == self.scroll_layout.itemAt(index).widget():
                item = self.scroll_layout.takeAt(index)
                item.widget().close()
                if self.scroll_layout.count() > 0:
                    self.scroll_layout.itemAt(0).widget().__show_labels__()
                return
            
    def __update_plot__(self, event):
        self.ax.cla()
        
        labels = []
        for index in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(index).widget()
            measurement = widget.measurements[widget.measurement_cb.currentIndex()]
            T = measurement.temperature
            H = measurement.field
            M = measurement.moment
            indices = (T >= widget.T_min_sb.value()) & (T <= widget.T_max_sb.value()) & \
                      (H >= widget.H_min_sb.value()) & (H <= widget.H_max_sb.value())
            self.ax.scatter(T[indices], M[indices], label=widget.label_le.text())
            labels.append(widget.label_le.text())
        self.ax.set_xlabel("Temperature [K]")
        self.ax.set_ylabel("Magnetisation [emu]")
        self.ax.yaxis.set_major_formatter('{x:.2e}')
        print(labels)
        if labels != [''] * len(labels):
            self.ax.legend()
        self.figure_canvas.draw()
