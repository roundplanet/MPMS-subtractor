# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:57:22 2025

@author: kaisjuli
"""
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox

class OpenMeasurementDialog(QDialog):
    
    def __init__(self, starting_dir : str = 'C:') -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/open_measurement_dialog.ui", self)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Cancel")
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.direct_mapping_cb.setEnabled(False)
        
        self.sample_filenames : None | list[str] = None
        self.background_filename : None | str = None
        self.sample_pb.clicked.connect(self.browse_sample_filename)
        self.background_pb.clicked.connect(self.browse_background_filename)
        self.starting_dir : str = starting_dir
        
    def browse_sample_filename(self, event):
        self.sample_filenames : list[str] = QFileDialog.getOpenFileNames(self, "Open sample file", self.starting_dir, "*.rw.dat")[0]
        print(self.sample_filenames)
        if len(self.sample_filenames) == 0:
            return
        self.sample_le.setText(", ".join([f.split("/")[-1] for f in self.sample_filenames]))
        self.background_le.setEnabled(True)
        self.background_pb.setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        
    def browse_background_filename(self, event):
        self.background_filename : str = QFileDialog.getOpenFileName(self, "Open background file", self.starting_dir, "*.rw.dat")[0]
        if self.background_filename == "":
            self.background_filename : None | str = None
            return
        self.background_le.setText(self.background_filename.split("/")[-1])
        self.direct_mapping_cb.setEnabled(True)