# -*- coding: utf-8 -*-
"""
Created on Tue May 13 09:21:06 2025

@author: kaisjuli
"""
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QWidget, QScrollArea, QDockWidget, QVBoxLayout, QTextEdit, QFileDialog
from PyQt5 import QtCore

import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from .measurementdataplot import MeasurementDataplot
from .openmeasurementdialog import OpenMeasurementDialog
from .openmeasurementfromscandialog import ConvertMeasurementFromScanDialog
from .convert_he3_raw_data_dialog import ConvertHe3RawDataDialog
from .filecollapsiblewidget import FileCollapsibleWidget
from .myqmdisubwindow import MyQMdiSubWindow
from .openplotdialog import OpenPlotDialog
from .multipleplotdialog import MultiplePlotDialog
from .constantsdialog import ConstantsDialog
from ..data import Measurement, MeasurementContainer

class MainWindow(QMainWindow):
    
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/main_window.ui", self)
        
        self.setCentralWidget(self.mdiArea)
        
        # setting up console
        self._console = QTextEdit()
        self._console.setReadOnly(True)
        
        date = QtCore.QDateTime.currentDateTime()
        self._console.append("<b>Starting log console, {0}</b><br />".format(date.toString()))
        
        # creating dockable pane for console
        self._console_pane = QDockWidget("Console", self)
        self._console_pane.setWidget(self._console)
        self._console_pane.resize(QtCore.QSize(450, 300))
        self._console_pane.setFeatures(QDockWidget.DockWidgetMovable)
        
        file_list_layout = QVBoxLayout()
        file_list_layout.setAlignment(QtCore.Qt.AlignTop)
        
        self._file_list = QWidget()
        self._file_list.setLayout(file_list_layout)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self._file_list)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll_area.resize(QtCore.QSize(450, 500))
        
        # creating dockable pane for files
        self._files_pane = QDockWidget("Files", self)
        self._files_pane.setWidget(scroll_area)
        self._files_pane.resize(QtCore.QSize(450, 600))
        self._files_pane.setFeatures(QDockWidget.DockWidgetMovable)
        
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self._files_pane)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self._console_pane)        

        self.starting_dir : str = "C:"
        self.actionOpen.triggered.connect(self.open_measurement)
        self.action_convert_scans.triggered.connect(self.convert_measurement_from_scan)
        self.action_He3_rw_dat_rw_dat.triggered.connect(self.convert_he3_raw_data)
        #self.actionNew.triggered.connect(self.plot_measurement)
        self.actionMultiple.triggered.connect(self.plot_multiple_measurement)
        self.actionclose_all.triggered.connect(self.close_all_mdi_subwindows)
        self.actionminimize_all.triggered.connect(self.minimize_all_mdi_subwindows)
        self.actioncascade.triggered.connect(self.cascade_all_mdi_subwindows)
        self.actiontile.triggered.connect(self.tile_all_mdi_subwindows)
        self.measurements : MeasurementContainer = MeasurementContainer()
        self.menuConstants.aboutToShow.connect(self.show_constants)
        
        self.showMaximized()
        
        
    def open_measurement(self):
        open_measurement_dialog = OpenMeasurementDialog(self.starting_dir)
        if open_measurement_dialog.exec():
            self.starting_dir : str = "/".join(open_measurement_dialog.sample_filenames[0].split()[:-1])
            for sample_filename in open_measurement_dialog.sample_filenames:
                self.add_measurement(sample_filename,
                                     open_measurement_dialog.background_filename,
                                     open_measurement_dialog.direct_mapping_cb.isChecked())
        
    def convert_measurement_from_scan(self):
        open_measurement_from_scan_dialog = ConvertMeasurementFromScanDialog()
        if open_measurement_from_scan_dialog.exec():
            open_measurement_from_scan_dialog.convert()
            
    def convert_he3_raw_data(self):
        convert_he3_raw_data_dialog = ConvertHe3RawDataDialog()
        if convert_he3_raw_data_dialog.exec():
            convert_he3_raw_data_dialog.convert()
    
    def add_measurement(self, sample_filename, background_filename, direct_mapping = True):
        measurement = self.measurements.add(sample_filename, background_filename, direct_mapping)
        
        collapsible = FileCollapsibleWidget(measurement)
        self._file_list.layout().addWidget(collapsible)
        
        sub = MyQMdiSubWindow([measurement], [collapsible], [None])
        self.mdiArea.addSubWindow(sub).show()
        collapsible.plot_windows.append(sub)
        
    def delete_measurement(self, measurement):         
        self.measurements.remove(measurement)
        for index in range(self._file_list.layout().count()):
            if measurement == self._file_list.layout().itemAt(index).widget().measurement:
                item = self._file_list.layout().takeAt(index)
                item.widget().close()
                return
               
    """
    deprecated
    
    def plot_measurement(self):
        open_plot_dialog = OpenPlotDialog(self.measurements)
        if open_plot_dialog.exec() and open_plot_dialog.measurement is not None:
            collapsible = None
            for index in range(self._file_list.layout().count()):
                if open_plot_dialog.measurement == self._file_list.layout().itemAt(index).widget().measurement:
                    collapsible = self._file_list.layout().itemAt(index).widget()
            sub = MyQMdiSubWindow([open_plot_dialog.measurement],
                                  [collapsible],
                                  [np.arange(open_plot_dialog.index_start_sb.value(),
                                            open_plot_dialog.index_end_sb.value() + 1)])
            self.mdiArea.addSubWindow(sub).show()
            collapsible.plot_windows.append(sub)
    """
        
    def plot_multiple_measurement(self):
        dialog = MultiplePlotDialog(self.measurements)
        if dialog.exec() and dialog.scroll_layout.count() > 0:
            widget_measurements = []
            widget_index_maps = []
            widget_labels = []
            widget_collapsibles = []
            for index in range(dialog.scroll_layout.count()):
                widget = dialog.scroll_layout.itemAt(index).widget()
                measurement = widget.measurements[widget.measurement_cb.currentIndex()]
                T = measurement.temperature
                H = measurement.field
                index_map = np.argwhere((T >= widget.T_min_sb.value()) & (T <= widget.T_max_sb.value()) & \
                                        (H >= widget.H_min_sb.value()) & (H <= widget.H_max_sb.value())).T[0]
                widget_labels.append(widget.label_le.text())
                for index in range(self._file_list.layout().count()):
                    if measurement == self._file_list.layout().itemAt(index).widget().measurement:
                        collapsible = self._file_list.layout().itemAt(index).widget()
                widget_measurements.append(measurement)
                widget_collapsibles.append(collapsible)
                widget_index_maps.append(index_map)
            sub = MyQMdiSubWindow(widget_measurements, widget_collapsibles, widget_index_maps, widget_labels)
            self.mdiArea.addSubWindow(sub).show()
            for collapsible in widget_collapsibles:
                collapsible.plot_windows.append(sub)
                
    def closeEvent(self, event):
        for subwindow in self.mdiArea.subWindowList():
            for dialog in reversed(subwindow.measurement_dataplot.dialogs):
                dialog.close()
        super().closeEvent(event)
                          
        
    def close_all_mdi_subwindows(self):
        self.mdiArea.closeAllSubWindows()
        for widget in self.mdiArea.subWindowList():
            self.mdiArea.removeSubWindow(widget)
        
    def minimize_all_mdi_subwindows(self):
        for window in self.mdiArea.subWindowList():
            window.showMinimized()
        
    def cascade_all_mdi_subwindows(self):
        self.mdiArea.cascadeSubWindows()
        
    def tile_all_mdi_subwindows(self):
        self.mdiArea.tileSubWindows()
        
    def show_constants(self):
        ConstantsDialog().exec()
        
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    Window = MainWindow()
    Window.show()
    sys.exit(app.exec())