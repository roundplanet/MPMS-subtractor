# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:57:22 2025

@author: kaisjuli
"""
import os

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox, QMessageBox

class OpenMeasurementDialog(QDialog):
    
    def __init__(self, starting_dir : str = 'C:') -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/open_measurement_dialog.ui", self)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Cancel")
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.direct_mapping_cb.setEnabled(False)
        self.constants_filename = "/".join(os.path.abspath(__file__).split("\\")[:-2]) + "/constants/MPMS3_constants.txt"
        self.constants_le.setText(self.constants_filename.split("/")[-1])
        print(self.constants_filename)
        
        self.sample_filenames : None | list[str] = None
        self.background_filename : None | str = None
        self.sample_pb.clicked.connect(self.browse_sample_filename)
        self.background_pb.clicked.connect(self.browse_background_filename)
        self.constants_pb.clicked.connect(self.browse_constants_filename)
        self.starting_dir : str = starting_dir
        
    def browse_sample_filename(self, event):
        self.sample_filenames : list[str] = QFileDialog.getOpenFileNames(self, "Open sample file", self.starting_dir, "*.rw.dat *.dc.raw")[0]
        print(self.sample_filenames)
        if len(self.sample_filenames) == 0:
            return
        self.sample_le.setText(", ".join([f.split("/")[-1] for f in self.sample_filenames]))
        self.background_le.setEnabled(True)
        self.background_pb.setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        
    def browse_background_filename(self, event):
        self.background_filename : str = QFileDialog.getOpenFileName(self, "Open background file", self.starting_dir, "*.rw.dat *.dc.raw")[0]
        if self.background_filename == "":
            self.background_filename : None | str = None
            return
        self.background_le.setText(self.background_filename.split("/")[-1])
        self.direct_mapping_cb.setEnabled(True)
        
    def browse_constants_filename(self, event):
        constants_filename : str = QFileDialog.getOpenFileName(self, "Open constants file", "/".join(os.path.abspath(__file__).split("\\")[:-2]) + "/constants/", "*.txt")[0]
        if constants_filename == "":
            return
        else:
            expected_constants = ["COIL_RADIUS", "COIL_DISTANCE", "SYSTEM_CALIBRATION", "DC_CALIBRATION_FACTOR"]
            constants = {}
            try:
                with open(constants_filename) as f:
                    for line in f:
                        if line.strip():
                            name, value = line.strip().split(",", 1)
                            constants[name] = float(value)
                            
            except ValueError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setWindowTitle("Error")
                msg.setText("The selected constants file structure is not valid!")
                msg.exec_()
                return
                        
            for key in expected_constants:
                if key not in constants:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setWindowTitle("Error")
                    msg.setText("The selected constants file is not valid. {} is missing!".format(key))
                    msg.exec_()
                    return
                    
        self.constants_filename = constants_filename + ""
        self.constants_le.setText(self.constants_filename.split("/")[-1])
        