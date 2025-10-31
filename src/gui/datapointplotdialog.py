# -*- coding: utf-8 -*-
"""
Created on Wed May 21 08:13:06 2025

@author: kaisjuli
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..data import Measurement
    from ..data import MeasurementDataPoint
    from .measurementdataplot import MeasurementDataplot
    
import os
import numpy as np
import pyperclip
    
from PyQt5 import uic
from PyQt5.QtWidgets import QDialog, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor, QPixmap
from PIL import Image, ImageQt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from ..calculation import gradiometer_function, gradiometer_function_fixed_center, subtract_background
from .datapointinfowidget import DatapointInfoWidget

class DatapointPlotDialog(QDialog):
    
    def __init__(self, parent : MeasurementDataplot, measurement : Measurement,
                 index_map : np.ndarray, index : int):
        super().__init__()
        file_prefix = "/".join(os.path.abspath(__file__).split("\\")[:-1]) + "/ui_files/"
        uic.loadUi(file_prefix + "/datapoint_plot_dialog.ui", self)

        self.parent = parent
        self.measurement = measurement
        self.index_map = index_map
        self.datapoint_subset = self.measurement.datapoint_subset(self.index_map)

        self.nr_labels = {"tl" : self.nr_tl_lb,
                          "tr" : self.nr_tr_lb,
                          "bl" : self.nr_bl_lb,
                          "br" : self.nr_br_lb}  
        self.amplitude_labels = {"tl" : self.amplitude_tl_lb,
                                 "tr" : self.amplitude_tr_lb,
                                 "bl" : self.amplitude_bl_lb,
                                 "br" : self.amplitude_br_lb}        
        self.drift_labels = {"tl" : self.drift_tl_lb,
                             "tr" : self.drift_tr_lb,
                             "bl" : self.drift_bl_lb,
                             "br" : self.drift_br_lb}   
        self.yoffset_labels = {"tl" : self.yoffset_tl_lb,
                               "tr" : self.yoffset_tr_lb,
                               "bl" : self.yoffset_bl_lb,
                               "br" : self.yoffset_br_lb}   
        self.xoffset_labels = {"tl" : self.xoffset_tl_lb,
                               "tr" : self.xoffset_tr_lb,
                               "bl" : self.xoffset_bl_lb,
                               "br" : self.xoffset_br_lb}   
        self.field_labels = {"tl" : self.field_tl_lb,
                             "tr" : self.field_tr_lb,
                             "bl" : self.field_bl_lb,
                             "br" : self.field_br_lb}   
        self.temp_labels = {"tl" : self.temp_tl_lb,
                            "tr" : self.temp_tr_lb,
                            "bl" : self.temp_bl_lb,
                             "br" : self.temp_br_lb}
        self.nr_spinboxes = {"tl" : self.nr_tl_sb,
                             "tr" : self.nr_tr_sb,
                             "bl" : self.nr_bl_sb,
                             "br" : self.nr_br_sb}
        self.scatter_items = {"tl" : None,
                             "tr" : None,
                             "bl" : None,
                             "br" : None}
        self.annotate_items = {"tl" : None,
                               "tr" : None,
                               "bl" : None,
                               "br" : None}
        self.datapoints = {"tl" : None,
                           "tr" : None,
                           "bl" : None,
                           "br" : None}
        self.indexes = {"tl" : None,
                        "tr" : None,
                        "bl" : None,
                        "br" : None}
        
        self.nr_toolboxes = {"tl" : self.nr_tl_tb,
                             "tr" : self.nr_tr_tb,
                             "bl" : self.nr_bl_tb,
                             "br" : self.nr_br_tb}
        
        
        
        self.__fill_legend_labels__(self.sample_img_lb, file_prefix + "green_diamond")
        self.__fill_legend_labels__(self.sample_fit_img_lb, file_prefix + "green_line")
        self.__fill_legend_labels__(self.background_img_lb, file_prefix + "red_diamond")
        self.__fill_legend_labels__(self.background_fit_img_lb, file_prefix + "red_line")
        self.__fill_legend_labels__(self.sample_wo_background_img_lb, file_prefix + "blue_diamond")
        self.__fill_legend_labels__(self.sample_wo_background_fit_img_lb, file_prefix + "blue_line")
        if self.measurement.background_rdf is None:
            for cb in [self.background_cb, self.background_fit_cb,
                       self.sample_wo_background_cb, self.sample_wo_background_fit_cb]:
                cb.setEnabled(False)
                cb.setChecked(False)
        for cb in [self.sample_cb, self.sample_fit_cb,
                   self.background_cb, self.background_fit_cb,
                   self.sample_wo_background_cb, self.sample_wo_background_fit_cb]:
            cb.stateChanged.connect(self.__set_datapoints_from_spinboxes__)
        
        for sb in self.nr_spinboxes.values():
            sb.setRange(0, len(self.index_map)-1)
        
        self.__init_popup_menu__()
        self.axes = {}
        self.figure_canvas = {}
        for i, place in enumerate(["tl", "tr", "bl", "br"]):
            figure = Figure()
            figure.set_layout_engine("tight")
            ax = figure.add_subplot(111)
            ax.set_xlabel("position [mm]")
            ax.set_ylabel("voltage [V]")
            #figure.tight_layout()
            figure_canvas = FigureCanvas(figure)
            self.gridLayout.addWidget(figure_canvas, i//2, i%2)
            self.axes.update({place : ax})
            self.figure_canvas.update({place : figure_canvas})
        self.figure_canvas["tl"].mpl_connect("button_press_event", self.__show_popup_menu_tl__)
        self.figure_canvas["tr"].mpl_connect("button_press_event", self.__show_popup_menu_tr__)
        self.figure_canvas["bl"].mpl_connect("button_press_event", self.__show_popup_menu_bl__)
        self.figure_canvas["br"].mpl_connect("button_press_event", self.__show_popup_menu_br__)
        self.__plot_multiple_datapoints__(index, index + 1, index + 2, index + 3)
        
        
        self.previous_large_pb.setText("\u25C4\u25C4\u25C4 (First)")
        self.previous_large_pb.clicked.connect(self.__previous_large_index_change__)
        self.previous_medium_pb.setText("\u25C4\u25C4 (-24)")
        self.previous_medium_pb.clicked.connect(self.__previous_medium_index_change__)
        self.previous_small_pb.setText("\u25C4 (-4)")
        self.previous_small_pb.clicked.connect(self.__previous_small_index_change__)
        self.previous_xsmall_pb.setText("\u25C5 (-1)")
        self.previous_xsmall_pb.clicked.connect(self.__previous_xsmall_index_change__)
        self.next_large_pb.setText("(Last) \u25BA\u25BA\u25BA")
        self.next_large_pb.clicked.connect(self.__next_large_index_change__)
        self.next_medium_pb.setText("(+24) \u25BA\u25BA")
        self.next_medium_pb.clicked.connect(self.__next_medium_index_change__)
        self.next_small_pb.setText("(+4) \u25BA")
        self.next_small_pb.clicked.connect(self.__next_small_index_change__)
        self.next_xsmall_pb.setText("(+1) \u25BB")
        self.next_xsmall_pb.clicked.connect(self.__next_xsmall_index_change__)
        self.go_pb.clicked.connect(self.__set_datapoints_from_spinboxes__)
        
        self.more_info_widget = DatapointInfoWidget(self)
        self.more_info_widget.hide()
        #for d in ["tl", "tr", "bl", "br"]:
        self.nr_tl_tb.clicked.connect(lambda event: self.__show_more_info__(event, "tl"))
        self.nr_tr_tb.clicked.connect(lambda event: self.__show_more_info__(event, "tr"))
        self.nr_bl_tb.clicked.connect(lambda event: self.__show_more_info__(event, "bl"))
        self.nr_br_tb.clicked.connect(lambda event: self.__show_more_info__(event, "br"))
        
    def __fill_legend_labels__(self, label, filename):
        pixmap = QPixmap(filename)
        scaled_pixmap = pixmap.scaled(label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        label.setPixmap(scaled_pixmap)
        
    def __plot_multiple_datapoints__(self, index1, index2, index3, index4):
        self.__plot_datapoint__(index1, "tl")
        self.__plot_datapoint__(index2, "tr")
        self.__plot_datapoint__(index3, "bl")
        self.__plot_datapoint__(index4, "br")
        
    def __correct_index__(self, index):
        return index % len(self.index_map)
        #return (index-self.parent.start_index)%(self.parent.end_index - self.parent.start_index) + self.parent.start_index
        
    def __plot_datapoint__(self, index, direction):
        index = self.__correct_index__(index)
        self.indexes[direction] = index
        datapoint = self.datapoint_subset[index]
        self.datapoints[direction] = datapoint
        self.__print_datapoint_info__(datapoint, index, direction)
        self.axes[direction].cla()
        self.axes[direction].set_xlabel("position [mm]")
        self.axes[direction].set_ylabel("voltage [V]")
        self.axes[direction].set_title("Datapoint #{}".format(index))
        
        if self.sample_cb.isChecked():
            self.axes[direction].scatter(datapoint.sample_rdp.raw_position,
                                         datapoint.sample_rdp.raw_voltage,
                                         marker="D", c="limegreen", s=10)
        if self.sample_fit_cb.isChecked():
            if self.parent.center_mode == "free":
                self.axes[direction].plot(datapoint.sample_rdp.raw_position,
                                          gradiometer_function(datapoint.sample_rdp.raw_position,
                                                               *datapoint.sample_result["fit_coeff"]),
                                          color="darkgreen")
            else:
                self.axes[direction].plot(datapoint.sample_rdp.raw_position,
                                          gradiometer_function_fixed_center(datapoint.sample_result["fixed_ctr"])(
                                              datapoint.sample_rdp.raw_position,                                                      
                                              *datapoint.sample_result["fit_fixed_ctr_coeff"]),
                                          color="darkgreen")
        if datapoint.background_rdp is not None:
            if self.background_cb.isChecked():
                self.axes[direction].scatter(datapoint.background_rdp.raw_position,
                                             datapoint.background_rdp.raw_voltage,
                                             marker="D", c="lightsalmon", s=10)
            if self.background_fit_cb.isChecked():
                if self.parent.center_mode == "free":
                    self.axes[direction].plot(datapoint.background_rdp.raw_position,
                                              gradiometer_function(datapoint.background_rdp.raw_position,
                                                                   *datapoint.background_result["fit_coeff"]),
                                              color="crimson")
                else:
                    self.axes[direction].plot(datapoint.background_rdp.raw_position,
                                              gradiometer_function_fixed_center(datapoint.background_result["fixed_ctr"])(
                                                  datapoint.background_rdp.raw_position,                                                      
                                                  *datapoint.background_result["fit_fixed_ctr_coeff"]),
                                              color="crimson")
                
            if self.sample_wo_background_cb.isChecked():
                self.axes[direction].scatter(*subtract_background(datapoint.sample_rdp,
                                                                  datapoint.background_rdp),
                                             marker="D", c="lightsteelblue", s=10)
            if self.sample_wo_background_fit_cb.isChecked():
                if self.parent.center_mode == "free":
                    self.axes[direction].plot(datapoint.sample_rdp.raw_position,
                                              gradiometer_function(datapoint.sample_rdp.raw_position,
                                                                   *datapoint.datapoint_result["fit_coeff"]),
                                              color="navy")
                else:
                    self.axes[direction].plot(datapoint.sample_rdp.raw_position,
                                              gradiometer_function_fixed_center(datapoint.datapoint_result["fixed_ctr"])(
                                                  datapoint.sample_rdp.raw_position,                                                      
                                                  *datapoint.datapoint_result["fit_fixed_ctr_coeff"]),
                                              color="navy")
        self.figure_canvas[direction].draw()
        
        self.draw_datapoint_on_parent(datapoint, direction, index)
        
        self.nr_spinboxes[direction].setValue(index)
        
    def draw_datapoint_on_parent(self, datapoint, direction, index, delete_old_point=True):
         if self.parent.temperature_dependent:
             x = datapoint.sample_rdp.temperature
         else:
             x = datapoint.sample_rdp.field
             
         mass = self.measurement.sample_rdf.sample_mass
         density = self.measurement.sample_rdf.sample_density
         molar_mass = self.measurement.sample_rdf.sample_molar_mass
         if self.parent.magnetisation_mode == "moment":
             if self.parent.center_mode == "free":
                 y = datapoint.datapoint_result["moment"]
             elif self.parent.center_mode == "fixed":
                 y = datapoint.datapoint_result["moment_fixed_ctr"]
         elif self.parent.magnetisation_mode == "moment mu bohr":
             if self.parent.center_mode == "free":
                 y = datapoint.datapoint_result["moment"]
             elif self.parent.center_mode == "fixed":
                 y = datapoint.datapoint_result["moment_fixed_ctr"]
             y = 1000 * y * float(self.measurement.sample_rdf.sample_molar_mass) / (float(self.measurement.sample_rdf.sample_mass) * 5585)
         elif self.parent.magnetisation_mode == "mass magnetisation":
             if self.parent.center_mode == "free":
                 y = datapoint.datapoint_result["moment"]
             elif self.parent.center_mode == "fixed":
                 y = datapoint.datapoint_result["moment_fixed_ctr"]
             y = 1000 * y / float(self.measurement.sample_rdf.sample_mass)
         elif self.parent.magnetisation_mode == "molar magnetisation":
             if self.parent.center_mode == "free":
                 y = datapoint.datapoint_result["moment"]
             elif self.parent.center_mode == "fixed":
                 y = datapoint.datapoint_result["moment_fixed_ctr"]
             y = 1000 * y / (float(self.measurement.sample_rdf.sample_mass) / float(self.measurement.sample_rdf.sample_molar_mass))
         elif self.parent.magnetisation_mode == "volume":
             if self.parent.center_mode == "free":
                 y = datapoint.convert_to_volume_susceptibility(mass, density)
             elif self.parent.center_mode == "fixed":
                 y = datapoint.convert_to_volume_susceptibility(mass, density, False)
         elif self.parent.magnetisation_mode == "mass":
             if self.parent.center_mode == "free":
                 y = datapoint.convert_to_mass_susceptibility(mass)
             elif self.parent.center_mode == "fixed":
                 y = datapoint.convert_to_mass_susceptibility(mass, False)
         elif self.parent.magnetisation_mode == "molar":
             if self.parent.center_mode == "free":
                 y = datapoint.convert_to_molar_susceptibility(mass, molar_mass)
             elif self.parent.center_mode == "fixed":
                 y = datapoint.convert_to_molar_susceptibility(mass, molar_mass, False)
         if self.parent.inverse:
            y = 1 / y
            
         if self.scatter_items[direction] is not None and delete_old_point:
             self.scatter_items[direction].remove()
         self.scatter_items[direction] = self.parent.ax.scatter(x, y, c="r")
         if self.annotate_items[direction] is not None and delete_old_point:
             self.annotate_items[direction].remove()
         self.annotate_items[direction] = self.parent.ax.annotate(str(index), (x, y))
         self.parent.figure_canvas.draw()
        
    def __print_datapoint_info__(self, datapoint, index, direction):
        def asign_text(label, value, error=None):
            def formatter(num):
                if abs(num) > 1e-1:
                    return str(round(num, 2))
                return f"{num:.2e}"
            
            if error is None:
                label.setText(formatter(value))
            else:
                label.setText(formatter(value) + " \u00B1 " + formatter(error))
                
        asign_text(self.nr_labels[direction], index)
        asign_text(self.amplitude_labels[direction],
                   datapoint.datapoint_result["fit_coeff"][0],
                   np.diag(datapoint.datapoint_result["fit_err"])[0])
        asign_text(self.drift_labels[direction],
                   datapoint.datapoint_result["fit_coeff"][2],
                   np.diag(datapoint.datapoint_result["fit_err"])[2])
        asign_text(self.yoffset_labels[direction],
                   datapoint.datapoint_result["fit_coeff"][1],
                   np.diag(datapoint.datapoint_result["fit_err"])[3])
        asign_text(self.xoffset_labels[direction],
                   datapoint.datapoint_result["fit_coeff"][3],
                   np.diag(datapoint.datapoint_result["fit_err"])[1])
        asign_text(self.field_labels[direction], datapoint.sample_rdp.field)
        asign_text(self.temp_labels[direction], datapoint.sample_rdp.temperature)
        
    def __previous_large_index_change__(self, event):
        self.__plot_multiple_datapoints__(0, 1, 2, 3)
        
    def __previous_medium_index_change__(self, event):
        for direction in ["tl", "tr", "bl", "br"]:
            self.__plot_datapoint__(self.indexes[direction] - 24, direction)
        
    def __previous_small_index_change__(self, event):
        for direction in ["tl", "tr", "bl", "br"]:
            self.__plot_datapoint__(self.indexes[direction] - 4, direction)
    
    def __previous_xsmall_index_change__(self, event):
        for direction in ["tl", "tr", "bl", "br"]:
            self.__plot_datapoint__(self.indexes[direction] - 1, direction)
        
    def __next_large_index_change__(self, event):
        self.__plot_multiple_datapoints__(len(self.index_map) - 4,
                                          len(self.index_map) - 3,
                                          len(self.index_map) - 2,
                                          len(self.index_map) - 1)
        
    def __next_medium_index_change__(self, event):
        for direction in ["tl", "tr", "bl", "br"]:
            self.__plot_datapoint__(self.indexes[direction] + 24, direction)
        
    def __next_small_index_change__(self, event):
        for direction in ["tl", "tr", "bl", "br"]:
            self.__plot_datapoint__(self.indexes[direction] + 4, direction)
            
    def __next_xsmall_index_change__(self, event):
        for direction in ["tl", "tr", "bl", "br"]:
            self.__plot_datapoint__(self.indexes[direction] + 1, direction)
            
    def __set_datapoints_from_spinboxes__(self, event):
        for direction in ["tl", "tr", "bl", "br"]:
            self.__plot_datapoint__(self.nr_spinboxes[direction].value(), direction)
            
    def __show_more_info__(self, event, direction):
        self.more_info_widget.hide()
        self.more_info_widget.display_infos(self.datapoint_subset[self.indexes[direction]], self.indexes[direction])
        self.more_info_widget.show_widget((self.nr_toolboxes[direction].x() + self.nr_toolboxes[direction].width(),
                                           self.nr_toolboxes[direction].y() + self.nr_toolboxes[direction].height()))
    
    def __init_popup_menu__(self):
        self.popMenu = QMenu(self)
        self.current_popup_direction = None
        
        self.copy_sample_action = self.popMenu.addAction("copy sample")
        self.copy_sample_action.triggered.connect(self.__copy_sample__)
        self.copy_sample_fit_action = self.popMenu.addAction("copy sample fit")
        self.copy_sample_fit_action.triggered.connect(self.__copy_sample_fit__)
        
        if self.measurement.background_rdf is not None:
            self.popMenu.addSeparator()
            
            self.copy_background_action = self.popMenu.addAction("copy background")
            self.copy_background_action.triggered.connect(self.__copy_background__)
            self.copy_background_fit_action = self.popMenu.addAction("copy background fit")
            self.copy_background_fit_action.triggered.connect(self.__copy_background_fit__)
            
            self.popMenu.addSeparator()
            
            self.copy_sample_without_background_action = self.popMenu.addAction("copy sample without background")
            self.copy_sample_without_background_action.triggered.connect(self.__copy_sample_without_background__)
            self.copy_sample_without_background_fit_action = self.popMenu.addAction("copy sample without background fit")
            self.copy_sample_without_background_fit_action.triggered.connect(self.__copy_sample_without_background_fit__)
    
    def __copy_sample__(self, event):
        dp = self.datapoints[self.current_popup_direction]
        final_string = ""
        for x, y in zip(dp.sample_rdp.raw_position, dp.sample_rdp.raw_voltage):
            final_string += "{}\t{}\n".format(x, y)
        pyperclip.copy(final_string)
        
    def __copy_sample_fit__(self, event):
        dp = self.datapoints[self.current_popup_direction]
        final_string = ""
        if self.parent.center_mode == "free":
            for x, y in zip(dp.sample_rdp.raw_position,
                            gradiometer_function(dp.sample_rdp.raw_position,
                                                 *dp.sample_result["fit_coeff"])):
                final_string += "{}\t{}\n".format(x, y)
        else:
            for x, y in zip(dp.sample_rdp.raw_position,
                            gradiometer_function_fixed_center(dp.sample_result["fixed_ctr"])(
                                dp.sample_rdp.raw_position,
                                *dp.sample_result["fit_coeff"])
                            ):
                final_string += "{}\t{}\n".format(x, y)
        pyperclip.copy(final_string)
        
    def __copy_background__(self, event):
        
        dp = self.datapoints[self.current_popup_direction]
        final_string = ""
        for x, y in zip(dp.background_rdp.raw_position, dp.background_rdp.raw_voltage):
            final_string += "{}\t{}\n".format(x, y)
        pyperclip.copy(final_string)
        
    def __copy_background_fit__(self, event):
        dp = self.datapoints[self.current_popup_direction]
        final_string = ""
        if self.parent.center_mode == "free":
            for x, y in zip(dp.background_rdp.raw_position,
                            gradiometer_function(dp.background_rdp.raw_position,
                                                 *dp.background_result["fit_coeff"])):
                final_string += "{}\t{}\n".format(x, y)
        else:
            for x, y in zip(dp.background_rdp.raw_position,
                            gradiometer_function_fixed_center(dp.background_result["fixed_ctr"])(
                                dp.background_rdp.raw_position,
                                *dp.background_result["fit_coeff"])
                            ):
                final_string += "{}\t{}\n".format(x, y)
        pyperclip.copy(final_string)
        
    def __copy_sample_without_background__(self, event):
        dp = self.datapoints[self.current_popup_direction]
        final_string = ""
        for x, y in zip(*subtract_background(dp.sample_rdp, dp.background_rdp)):
            final_string += "{}\t{}\n".format(x, y)
        pyperclip.copy(final_string)
        
    def __copy_sample_without_background_fit__(self, event):
        dp = self.datapoints[self.current_popup_direction]
        final_string = ""
        if self.parent.center_mode == "free":
            for x, y in zip(dp.sample_rdp.raw_position,
                            gradiometer_function(dp.sample_rdp.raw_position,
                                                 *dp.datapoint_result["fit_coeff"])):
                final_string += "{}\t{}\n".format(x, y)
        else:
            for x, y in zip(dp.sample_rdp.raw_position,
                            gradiometer_function_fixed_center(dp.datapoint_result["fixed_ctr"])(
                                dp.sample_rdp.raw_position,                                                      
                                *dp.datapoint_result["fit_fixed_ctr_coeff"])
                            ):
                final_string += "{}\t{}\n".format(x, y)
        pyperclip.copy(final_string)
            
    def __show_popup_menu_tl__(self, event):
        if event.button == 3:
            cursor = QCursor()
            self.current_popup_direction = "tl"
            self.popMenu.popup(cursor.pos())
            
    def __show_popup_menu_tr__(self, event):
        if event.button == 3:
            cursor = QCursor()
            self.current_popup_direction = "tr"
            self.popMenu.popup(cursor.pos())
            
    def __show_popup_menu_bl__(self, event):
        if event.button == 3:
            cursor = QCursor()
            self.current_popup_direction = "bl"
            self.popMenu.popup(cursor.pos())
            
    def __show_popup_menu_br__(self, event):
        if event.button == 3:
            cursor = QCursor()
            self.current_popup_direction = "br"
            self.popMenu.popup(cursor.pos())
    
    def closeEvent(self, event):
        for scatter_item in self.scatter_items.values():
            scatter_item.remove()
        for annotate_item in self.annotate_items.values():
            annotate_item.remove()
        self.parent.dialogs.remove(self)
        self.parent.figure_canvas.draw()
        
#DatapointPlotDialog(None, None, None).exec()