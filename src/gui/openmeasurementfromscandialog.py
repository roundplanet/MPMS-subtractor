# -*- coding: utf-8 -*-
"""
Created on Thu May 15 15:57:22 2025

@author: kaisjuli
"""
import os
import numpy as np

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox

class ConvertMeasurementFromScanDialog(QDialog):
    
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/open_measurement_from_scan_dialog.ui", self)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Cancel")
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
        self.sample_filename : None | str = None
        self.logfile_filename : None | str = None
        self.save_filename : None | str = None
        self.sample_pb.clicked.connect(self.browse_sample_filename)
        self.logfile_pb.clicked.connect(self.browse_logfile_filename)
        self.save_filename_pb.clicked.connect(self.browse_save_filename)
        
    def browse_sample_filename(self, event):
        self.sample_filename : str = QFileDialog.getOpenFileName(self, "Open sample file", 'C:', "*scans.rw.dat")[0]
        if self.sample_filename == "":
            return
        self.sample_le.setText(self.sample_filename.split("/")[-1])
        if self.logfile_filename is not None and self.save_filename is not None:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        
    def browse_logfile_filename(self, event):
        self.logfile_filename : str = QFileDialog.getOpenFileName(self, "Open logfile", 'C:', "*.dat")[0]
        self.logfile_le.setText(self.logfile_filename.split("/")[-1])
        if self.sample_filename is not None and self.save_filename is not None:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            
    def browse_save_filename(self, event):
        self.save_filename : str = QFileDialog.getSaveFileName(self, "Save converted file", 'C:', "*.rw.dat")[0]
        if self.save_filename == "":
            return
        self.save_filename_le.setText(self.save_filename.split("/")[-1])
        if self.sample_filename is not None and self.logfile_filename is not None:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            
    def convert(self):
        scan_data = np.loadtxt(self.sample_filename, skiprows=30, delimiter=",", usecols=(1,2,3))
        logdata = np.loadtxt(self.logfile_filename, skiprows=20, usecols=(1,2,3,24), delimiter=",")
        indizes = []
        
        for i in range(scan_data.shape[0] - 1):
            if scan_data[i, 0] != scan_data[i+1, 0]:
                indizes.append(i+1)
                
        data_chunks = np.split(scan_data, indizes)

        lines = []
        with open(self.sample_filename, 'r') as file:
            for line in file:
                lines.append(line)
                if "Comment," in line:
                    break

        for data_chunk in data_chunks:
            timestamp = data_chunk[2, 0]
            _, temp, field, range_ = logdata[np.argmin(np.abs(logdata[:, 0] - timestamp)), :]
            s = ";low temp = {} K;high temp = {} K;avg. temp = {} K;low field = {} Oe;high field = {} Oe;drift = 0 V/s;slope = 0 V/mm;squid range = {};given center = {} mm;calculated center = {} mm;amp fixed = 0 V;amp free = 0 V\n"
            lines.append(s.format(temp,
                                  temp,
                                  temp,
                                  field,
                                  field,
                                  range_,
                                  self.center_dsb.value(),
                                  self.center_dsb.value()))
            for d in data_chunk:
                lines.append(",{},{},{},0\n".format(*d))
                
        with open(self.save_filename, 'w') as file:
            file.writelines(lines)