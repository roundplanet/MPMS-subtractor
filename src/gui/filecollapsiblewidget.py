# -*- coding: utf-8 -*-
"""
Created on Mon May 19 13:07:16 2025

@author: kaisjuli
"""

import os
import numpy as np

from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QLabel, QMessageBox, QFileDialog, QInputDialog
from PyQt5 import QtCore

from ..calculation import gradiometer_function, gradiometer_function_fixed_center, subtract_background

class FileCollapsibleWidget(QWidget):
    
    def __init__(self, measurement) -> None:
        super().__init__()
        uic.loadUi("/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/file_collapsible_widget.ui", self)
        
        self.measurement = measurement
        self.measurement_tb.setText(measurement.sample_rdf.filename.split("/")[-1])
        
        self.groupBox.hide()
        self.context_widget.hide()
        self.__fill_context_widget__()
        self.measurement_tb.clicked.connect(self.__hide_show_context__)
        
        self.plot_windows = []
        self.remove_pb.clicked.connect(self.__remove_from_list__)
        self.change_bg_pb.clicked.connect(self.__change_bg__)
        self.set_density_pb.clicked.connect(self.__set_density__)
        self.set_molar_mass_pb.clicked.connect(self.__set_molar_mass__)
        self.export_pb.clicked.connect(self.__export_measurement__)
        
        self.context_widget.layout().itemAt(4).widget().setParent(None)
        
    def insert_one_row(self, label_str, content_str):
        row_count = self.context_widget.layout().rowCount()
        label = QLabel(label_str)
        label.setWordWrap(True)
        self.context_widget.layout().addWidget(label, row_count, 0)
        label = QLabel(content_str)
        label.setWordWrap(True)
        self.context_widget.layout().addWidget(label, row_count, 1)    
            
    def __fill_context_widget__(self):
        self.insert_one_row("title", self.measurement.sample_rdf.title)
        self.insert_one_row("number of datapoints", str(len(self.measurement.sample_rdf)))
        self.insert_one_row("jump corrections", str(self.measurement.nr_jump_corrected_datapoints))
        self.insert_one_row("nonmatching datapoints", str(self.measurement.nr_not_matching_datapoints))
        self.insert_one_row("background selected", str(True if self.measurement.background_rdf is not None else False))
        self.insert_one_row("material", str(self.measurement.sample_rdf.sample_material))
        self.insert_one_row("comment", str(self.measurement.sample_rdf.sample_comment))
        self.insert_one_row("mass", str(self.measurement.sample_rdf.sample_mass) + " mg")
        self.insert_one_row("density", str(self.measurement.sample_rdf.sample_density) + " g/cm^3")
        self.insert_one_row("molar mass", str(self.measurement.sample_rdf.sample_molar_mass) + " g/mol")
        self.insert_one_row("sample holder", str(self.measurement.sample_rdf.sample_holder))
        self.insert_one_row("sample holder detail", str(self.measurement.sample_rdf.sample_holder_detail))
        self.insert_one_row("offset", str(self.measurement.sample_rdf.sample_offset) + " mm")
        self.context_widget.layout().addWidget(self.export_pb, self.context_widget.layout().rowCount(), 0, 1, -1)
    
    def __refill_context_widget__(self):
        for i in reversed(range(4, self.context_widget.layout().count())):
            self.context_widget.layout().itemAt(i).widget().setParent(None)
        self.__fill_context_widget__()
            
    def __hide_show_context__(self, event):
        if self.context_widget.isHidden():
            self.groupBox.show()
            self.context_widget.show()
            self.measurement_tb.setArrowType(QtCore.Qt.UpArrow)
        else:
            self.groupBox.hide()
            self.context_widget.hide()
            self.measurement_tb.setArrowType(QtCore.Qt.DownArrow)
            
    def __remove_from_list__(self, event):
        msg = QMessageBox(self.window())
        msg.setWindowTitle("Remove " + self.measurement.sample_rdf.filename.split("/")[-1])
        msg.setText("Are you sure you want to remove the file from the file list and close all related windows?")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        if msg.exec() == 1024:
            for plot_window in self.plot_windows:
                plot_window.skip_plot_remove = True
                plot_window.close()
            self.window().delete_measurement(self.measurement)
            
    def __change_bg__(self, event):
        new_bg_filename : str = QFileDialog.getOpenFileName(self, "Select new background file", 'C:', "*.rw.dat")[0]
        if new_bg_filename == "":
            return
        self.measurement.__set_background_rdf__(new_bg_filename)
        self.measurement.__create_measurement_datapoints__()
        self.__refill_context_widget__()
        for plot_window in self.plot_windows:
            for dialog in plot_window.measurement_dataplot.dialogs:
                dialog.close()
            plot_window.measurement_dataplot.ax.cla()
            for measurement, index_map, label in zip(plot_window.measurement_dataplot.measurements,
                                                     plot_window.measurement_dataplot.index_maps,
                                                     plot_window.measurement_dataplot.labels):
                plot_window.measurement_dataplot.plot_measurement_data(measurement, index_map, label)
            plot_window.measurement_dataplot.figure_canvas.draw()
            
    def __set_density__(self, event):
        answ = QInputDialog.getDouble(self, "New density", "Enter new sample density [g/cm^3]", 0, 0, 1000, 3)
        if answ[1]:
            self.measurement.sample_rdf.set_sample_density(answ[0])
            self.__refill_context_widget__()
            
    def __set_molar_mass__(self, event):
        answ = QInputDialog.getDouble(self, "New molar mass", "Enter new molar mass [g/mol]", 0, 0, 1000, 3)
        if answ[1]:
            self.measurement.sample_rdf.set_sample_molar_mass(answ[0])
            self.__refill_context_widget__()
            
    def __export_measurement__(self, event):
        export_filename : str = QFileDialog.getSaveFileName(self, "Export measurement", 'C:', "*.rw.dat *.dat")[0]
        if export_filename == "":
            return
        export_filename = export_filename.replace(".rw.dat", '').replace(".dat", '')
        
        with open(export_filename + ".dat", "w") as file:
            file.write("[Header]\n")
            file.write("TITLE,{}\n".format(self.measurement.sample_rdf.title))
            file.write("INFO,{},APPNAME\n".format(str(self.measurement.sample_rdf.appname)))
            file.write("INFO,{},SAMPLE_MATERIAL\n".format(str(self.measurement.sample_rdf.sample_material)))
            file.write("INFO,{},SAMPLE_COMMENT\n".format(str(self.measurement.sample_rdf.sample_comment)))
            file.write("INFO,{},SAMPLE_MASS\n".format(str(self.measurement.sample_rdf.sample_mass)))
            file.write("INFO,{},SAMPLE_VOLUME\n".format(str(self.measurement.sample_rdf.sample_volume)))
            file.write("INFO,{},SAMPLE_DENSITY\n".format(str(self.measurement.sample_rdf.sample_density)))
            file.write("INFO,{},SAMPLE_MOLECULAR_WEIGHT\n".format(str(self.measurement.sample_rdf.sample_molecular_weight)))
            file.write("INFO,{},SAMPLE_SIZE\n".format(str(self.measurement.sample_rdf.sample_size)))
            file.write("INFO,{},SAMPLE_SHAPE\n".format(str(self.measurement.sample_rdf.sample_shape)))
            file.write("INFO,{},SAMPLE_HOLDER\n".format(str(self.measurement.sample_rdf.sample_holder)))
            file.write("INFO,{},SAMPLE_HOLDER_DETAIL\n".format(str(self.measurement.sample_rdf.sample_holder_detail)))
            file.write("INFO,{},SAMPLE_OFFSET\n".format(str(self.measurement.sample_rdf.sample_offset)))
            file.write("[Data]\n")
            file.write("Time Stamp (sec),Temperature (K),Magnetic Field (Oe)," \
                       "DC Moment Fixed Ctr (emu),DC Moment Err Fixed Ctr (emu),DC Moment Fixed Ctr avg (emu),DC Moment Err Fixed Ctr avg (emu)," \
                       "DC Moment Free Ctr (emu), DC Moment Err Free Ctr (emu),DC Moment Free Ctr avg (emu), DC Moment Err Free Ctr avg (emu)\n")
            for mdp1, mdp2 in zip(self.measurement, self.measurement[1:] + [None]):
                if mdp2 is not None and mdp1.sample_rdp.temperature == mdp2.sample_rdp.temperature and mdp1.sample_rdp.field == mdp2.sample_rdp.field:
                    file.write(",".join([str(np.mean(mdp1.sample_rdp.timestamp)),
                                         str(mdp1.sample_rdp.temperature),
                                         str(mdp1.sample_rdp.field),
                                         str(mdp1.datapoint_result["moment_fixed_ctr"]),
                                         str(mdp1.datapoint_result["moment_fixed_ctr_err"]),
                                         str(np.mean([mdp1.datapoint_result["moment_fixed_ctr"], mdp2.datapoint_result["moment_fixed_ctr"]])),
                                         str(0.5*np.sqrt(mdp1.datapoint_result["moment_fixed_ctr_err"]**2 + mdp2.datapoint_result["moment_fixed_ctr_err"]**2)),
                                         str(mdp1.datapoint_result["moment"]),
                                         str(mdp1.datapoint_result["moment_err"]),
                                         str(np.mean([mdp1.datapoint_result["moment"], mdp2.datapoint_result["moment"]])),
                                         str(0.5*np.sqrt(mdp1.datapoint_result["moment_err"]**2 + mdp2.datapoint_result["moment_err"]**2))]) + "\n")
                else:
                    file.write(",".join([str(np.mean(mdp1.sample_rdp.timestamp)),
                                         str(mdp1.sample_rdp.temperature),
                                         str(mdp1.sample_rdp.field),
                                         str(mdp1.datapoint_result["moment_fixed_ctr"]),
                                         str(mdp1.datapoint_result["moment_fixed_ctr_err"]),
                                         str(""),
                                         str(""),
                                         str(mdp1.datapoint_result["moment"]),
                                         str(mdp1.datapoint_result["moment_err"]),
                                         str(""),
                                         str("")]) + "\n")
                
        with open(export_filename + ".rw.dat", "w") as file:
            file.write("[Header]\n")
            file.write("TITLE,{}\n".format(self.measurement.sample_rdf.title))
            file.write("INFO,{},APPNAME\n".format(str(self.measurement.sample_rdf.appname)))
            file.write("INFO,{},SAMPLE_MATERIAL\n".format(str(self.measurement.sample_rdf.sample_material)))
            file.write("INFO,{},SAMPLE_COMMENT\n".format(str(self.measurement.sample_rdf.sample_comment)))
            file.write("INFO,{},SAMPLE_MASS\n".format(str(self.measurement.sample_rdf.sample_mass)))
            file.write("INFO,{},SAMPLE_VOLUME\n".format(str(self.measurement.sample_rdf.sample_volume)))
            file.write("INFO,{},SAMPLE_DENSITY\n".format(str(self.measurement.sample_rdf.sample_density)))
            file.write("INFO,{},SAMPLE_MOLECULAR_WEIGHT\n".format(str(self.measurement.sample_rdf.sample_molecular_weight)))
            file.write("INFO,{},SAMPLE_SIZE\n".format(str(self.measurement.sample_rdf.sample_size)))
            file.write("INFO,{},SAMPLE_SHAPE\n".format(str(self.measurement.sample_rdf.sample_shape)))
            file.write("INFO,{},SAMPLE_HOLDER\n".format(str(self.measurement.sample_rdf.sample_holder)))
            file.write("INFO,{},SAMPLE_HOLDER_DETAIL\n".format(str(self.measurement.sample_rdf.sample_holder_detail)))
            file.write("INFO,{},SAMPLE_OFFSET\n".format(str(self.measurement.sample_rdf.sample_offset)))
            file.write("[Data]\n")
            file.write("Comment," \
                       "Sample Time Stamp (sec),Sample Raw Position (mm),Sample Raw Voltage (V),Sample Processed Voltage (V),Sample Fixed C Fitted (V),Sample Free C Fitted (V)," \
                       "Background Time Stamp (sec),Background Raw Position (mm),Background Raw Voltage (V),Background Processed Voltage (V),Background Fixed C Fitted (V),Background Free C Fitted (V)," \
                       "Subtracted Raw Position (mm),Subtracted Raw Voltage (V),Subtracted Fixed C Fitted (V),Subtracted Free C Fitted (V)\n")
            bg = True if self.measurement.background_rdf is not None else False
            for mdp in self.measurement:
                file.write(";".join(["",
                                     "low temp sample = {} K".format(mdp.sample_rdp.low_temp),
                                     "low temp background = {} K".format(mdp.background_rdp.low_temp if bg else ''),
                                     "high temp sample = {} K".format(mdp.sample_rdp.high_temp),
                                     "high temp background = {} K".format(mdp.background_rdp.high_temp if bg else ''),
                                     "avg. temp sample = {} K".format(mdp.sample_rdp.avg_temp),
                                     "avg. temp background = {} K".format(mdp.background_rdp.avg_temp if bg else ''),
                                     "low field sample = {} Oe".format(mdp.sample_rdp.low_field),
                                     "low field background = {} Oe".format(mdp.background_rdp.low_field if bg else ''),
                                     "high field sample = {} Oe".format(mdp.sample_rdp.high_field),
                                     "high field background = {} Oe".format(mdp.background_rdp.high_field if bg else ''),
                                     "drift sample = {} V/s".format(mdp.sample_rdp.drift),
                                     "drift background = {} V/s".format(mdp.background_rdp.drift if bg else ''),
                                     "slope sample = {} V/mm".format(mdp.sample_rdp.slope),
                                     "slope background = {} V/mm".format(mdp.background_rdp.slope if bg else ''),
                                     "squid range sample = {}".format(mdp.sample_rdp.squid_range),
                                     "squid range background = {}".format(mdp.background_rdp.squid_range if bg else ''),
                                     "given center sample = {} mm".format(mdp.sample_rdp.given_center),
                                     "given center background = {} mm".format(mdp.background_rdp.given_center if bg else ''),
                                     "calculated center sample = {} mm".format(mdp.sample_result["fit_coeff"][-1]),
                                     "calculated center background = {} mm".format(mdp.background_result["fit_coeff"][-1] if bg else ''),
                                     "calculated center subtracted = {} mm".format(mdp.datapoint_result["fit_coeff"][-1] if bg else ''),
                                     "amp fixed sample = {} V".format(mdp.sample_result["fit_coeff"][0]),
                                     "amp fixed background = {} V".format(mdp.background_result["fit_coeff"][0] if bg else ''),
                                     "amp fixed subtracted = {} V".format(mdp.datapoint_result["fit_coeff"][0] if bg else ''),
                                     "amp free sample = {} V".format(mdp.sample_result["fit_fixed_ctr_coeff"][0]),
                                     "amp free background = {} V".format(mdp.background_result["fit_fixed_ctr_coeff"][0] if bg else ''),
                                     "amp free subtracted = {} V".format(mdp.datapoint_result["fit_fixed_ctr_coeff"][0] if bg else '')]) + "\n")
                sample_fixed_c_fitted = gradiometer_function_fixed_center(mdp.sample_result["fixed_ctr"])(
                    mdp.sample_rdp.raw_position,                                                      
                    *mdp.sample_result["fit_fixed_ctr_coeff"]
                )
                sample_free_c_fitted = gradiometer_function(mdp.sample_rdp.raw_position,
                                                            *mdp.sample_result["fit_coeff"])
                for index in range(len(mdp.sample_rdp.timestamp)):
                    file.write(",".join([str(''),
                                         str(mdp.sample_rdp.timestamp[index]),
                                         str(mdp.sample_rdp.raw_position[index]),
                                         str(mdp.sample_rdp.raw_voltage[index]),
                                         str(mdp.sample_rdp.processed_voltage[index]),
                                         str(sample_fixed_c_fitted[index]),
                                         str(sample_free_c_fitted[index])]) + ','*10 + '\n')
                if bg:
                    background_fixed_c_fitted = gradiometer_function_fixed_center(mdp.background_result["fixed_ctr"])(
                        mdp.background_rdp.raw_position,                                                      
                        *mdp.background_result["fit_fixed_ctr_coeff"]
                    )
                    background_free_c_fitted = gradiometer_function(mdp.background_rdp.raw_position,
                                                                    *mdp.background_result["fit_coeff"])
                    for index in range(len(mdp.background_rdp.timestamp)):
                        file.write(","*7 + ",".join([str(mdp.background_rdp.timestamp[index]),
                                                     str(mdp.background_rdp.raw_position[index]),
                                                     str(mdp.background_rdp.raw_voltage[index]),
                                                     str(mdp.background_rdp.processed_voltage[index]),
                                                     str(background_fixed_c_fitted[index]),
                                                     str(background_free_c_fitted[index])]) + ','*4 + "\n")
                    
                    pos_wo_bg, voltage_wo_bg = subtract_background(mdp.sample_rdp, mdp.background_rdp)
                    subtracted_fixed_c_fitted = gradiometer_function_fixed_center(mdp.datapoint_result["fixed_ctr"])(
                        pos_wo_bg,                                                      
                        *mdp.datapoint_result["fit_fixed_ctr_coeff"]
                    )
                    subtracted_free_c_fitted = gradiometer_function(pos_wo_bg,
                                                                    *mdp.datapoint_result["fit_coeff"])
                    for index in range(len(pos_wo_bg)):
                        file.write(","*13 + ",".join([str(pos_wo_bg[index]),
                                                      str(voltage_wo_bg[index]),
                                                      str(subtracted_fixed_c_fitted[index]),
                                                      str(subtracted_free_c_fitted[index])]) + "\n")