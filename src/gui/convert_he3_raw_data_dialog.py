# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 13:39:13 2025

@author: kaisjuli
"""

import os
import numpy as np

from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox

class ConvertHe3RawDataDialog(QDialog):
    
    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/convert_he3_raw_data_dialog.ui", self)
        self.buttonBox.button(QDialogButtonBox.Cancel).setText("Cancel")
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        
        self.sample_filename : None | str = None
        self.sample_raw_filename : None | str = None
        self.save_filename : None | str = None
        self.sample_pb.clicked.connect(self.browse_sample_filename)
        self.sample_raw_pb.clicked.connect(self.browse_sample_raw_filename)
        self.save_filename_pb.clicked.connect(self.browse_save_filename)
        
    def browse_sample_filename(self, event):
        self.sample_filename : str = QFileDialog.getOpenFileName(self, "Open sample file", 'C:', "*.dat")[0]
        if self.sample_filename == "":
            return
        self.sample_le.setText(self.sample_filename.split("/")[-1])
        if self.sample_raw_filename is not None and self.save_filename is not None:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        
    def browse_sample_raw_filename(self, event):
        self.sample_raw_filename : str = QFileDialog.getOpenFileName(self, "Open sample raw file", 'C:', "*.rw.dat")[0]
        self.sample_raw_le.setText(self.sample_raw_filename.split("/")[-1])
        if self.sample_filename is not None and self.save_filename is not None:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            
    def browse_save_filename(self, event):
        self.save_filename : str = QFileDialog.getSaveFileName(self, "Save converted file", 'C:', "*.rw.dat")[0]
        if self.save_filename == "":
            return
        self.save_filename_le.setText(self.save_filename.split("/")[-1])
        if self.sample_filename is not None and self.sample_raw_filename is not None:
            self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
            
    def convert(self):
        data = np.loadtxt(self.sample_filename, skiprows=45, delimiter=",", usecols=(1,72))
        
        lines = []
        
        with open(self.sample_raw_filename, 'r') as file:
            info_line = None
            last_time = 0.0
            header_over = False
            for line in file:
                if header_over:
                    if "," in line:
                        timestamp = float(line.split(",")[1])
                    if info_line is not None:
                        cache_1 = info_line.split(";")
                        temp = data[np.argmin(np.abs(data[:, 0] - timestamp)), 1]
                        for i in [1, 2, 3]:
                            cache_2 = cache_1[i].split(" ")
                            cache_2[-2] = str(temp)
                            cache_1[i] = " ".join(cache_2)
                        info_line = ";".join(cache_1)
                        lines.append(info_line)
                        info_line = None
                    if "low temp" in line:
                        info_line = "" + line  
                    if "," in line:
                        lines.append(line)
                else:
                    if "Comment,Time" in line:
                        header_over = True
                    lines.append(line)

        with open(self.save_filename, 'w') as file:
            file.writelines(lines)