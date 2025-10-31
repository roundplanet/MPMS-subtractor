# -*- coding: utf-8 -*-
"""
Created on Tue May 20 08:31:41 2025

@author: kaisjuli
"""
from PyQt5.QtWidgets import QMdiSubWindow

from .measurementdataplot import MeasurementDataplot

class MyQMdiSubWindow(QMdiSubWindow):
    
    def __init__(self, measurements, collapsibles, index_maps, labels=None):
        super().__init__()
        self.measurement_dataplot = MeasurementDataplot(measurements, index_maps, labels)
        if len(measurements) == 1:
            self.setWindowTitle(measurements[0].sample_rdf.filename.split("/")[-1])
        self.setWidget(self.measurement_dataplot)
        self.collapsibles = collapsibles
        self.skip_plot_remove = False
        
    def closeEvent(self, event):
        if not self.skip_plot_remove:
            for collapsible in self.collapsibles:
                if self in collapsible.plot_windows:
                    collapsible.plot_windows.remove(self)
        for dialog in reversed(self.measurement_dataplot.dialogs):
            dialog.close()
        super().closeEvent(event)