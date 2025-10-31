# -*- coding: utf-8 -*-
"""
Created on Wed May 14 14:44:37 2025

@author: kaisjuli
"""
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ..data import Measurement
    
import numpy as np
    
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMenu, QActionGroup
from PyQt5.QtGui import QCursor

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from .datapointplot import DatapointPlot
from .datapointplotdialog import DatapointPlotDialog

class MeasurementDataplot(QWidget):
    
    def __init__(self, measurements : list[Measurement], index_maps : list[np.ndarray | None],
                 labels : list[str] = None):
        super().__init__()
        
        self.dialogs = []
        self.temperature_dependent = True
        self.magnetisation_mode = "moment"
        self.center_mode = "free"
        self.inverse = False
        self.log_x = False
        self.log_y = False
        
        self.__init_widget__()
        self.__init_popup_menu__()
        
        if labels is None:
            labels = [None] * len(measurements)
        
        self.measurements = measurements
        self.index_maps = index_maps
        self.labels = labels
        for measurement, index_map, label in zip(measurements, index_maps, labels):
            self.plot_measurement_data(measurement, index_map, label)
        if labels != [''] * len(measurements) and labels != [None] * len(measurements):
            self.__init_legend__()
        
        self.figure_canvas.mpl_connect("pick_event", self.actionClick)
        self.figure_canvas.mpl_connect("button_press_event", self.actionClick2)
    
    def __init_widget__(self):
        self.figure = Figure()
        self.figure_canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.figure_canvas, self)
        
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.figure_canvas)
        self.setLayout(layout)
        
        self.ax = self.figure.add_subplot(111)
        self.ax.yaxis.set_major_formatter('{x:.2e}')
        self.ax.set_xlabel("Temperature [K]")
        self.ax.set_ylabel("Magnetisation [emu]")
        self.figure.set_layout_engine("tight")
        #self.figure_canvas.draw()
        
    def __init_legend__(self):
        self.legend = self.ax.legend()
        for handler in self.legend.legend_handles:
            handler.set_picker(True)
            handler.in_legend = True
        self.map_legend_to_scatter = {}
        for handler, scatter in zip(self.legend.legend_handles, self.ax.collections):
            handler.set_alpha(1.0)
            self.map_legend_to_scatter[handler] = scatter
        
        
    def plot_measurement_data(self, measurement, index_map, label=None):
        index_map : np.ndarray = index_map if index_map is not None else np.arange(len(measurement))
        
        if self.temperature_dependent:
            x = measurement.temperature_subset(index_map)
        else:
            x = measurement.field_subset(index_map)
            
        if self.magnetisation_mode == "moment":
            if self.center_mode == "free":
                y = measurement.moment_subset(index_map)
            elif self.center_mode == "fixed":
                y = measurement.moment_fixed_ctr_subset(index_map)
        elif self.magnetisation_mode == "moment mu bohr":
            if self.center_mode == "free":
                y = measurement.moment_subset(index_map)
            elif self.center_mode == "fixed":
                y = measurement.moment_fixed_ctr_subset(index_map)
            y = 1000 * y * float(measurement.sample_rdf.sample_molar_mass) / (float(measurement.sample_rdf.sample_mass) * 5585)
        elif self.magnetisation_mode == "mass magnetisation":
            if self.center_mode == "free":
                y = measurement.moment_subset(index_map)
            elif self.center_mode == "fixed":
                y = measurement.moment_fixed_ctr_subset(index_map)
            y = 1000 * y / float(measurement.sample_rdf.sample_mass)
        elif self.magnetisation_mode == "molar magnetisation":
            if self.center_mode == "free":
                y = measurement.moment_subset(index_map)
            elif self.center_mode == "fixed":
                y = measurement.moment_fixed_ctr_subset(index_map)
            y = y / (float(measurement.sample_rdf.sample_mass) / (1000 * float(measurement.sample_rdf.sample_molar_mass)))
        elif self.magnetisation_mode == "volume":
            if self.center_mode == "free":
                y = measurement.volume_susceptibility_subset(index_map)
            elif self.center_mode == "fixed":
                y = measurement.volume_susceptibility_fixed_ctr_subset(index_map)
        elif self.magnetisation_mode == "mass":
            if self.center_mode == "free":
                y = measurement.mass_susceptibility_subset(index_map)
            elif self.center_mode == "fixed":
                y = measurement.mass_susceptibility_fixed_ctr_subset(index_map)
        elif self.magnetisation_mode == "molar":
            if self.center_mode == "free":
                y = measurement.molar_susceptibility_subset(index_map)
            elif self.center_mode == "fixed":
                y = measurement.molar_susceptibility_fixed_ctr_subset(index_map)
            
        artist = self.ax.scatter(x,
                                 1/y if self.inverse else y,
                                 label = label,
                                 picker = True)
        artist.measurement = measurement
        artist.in_legend = False
        artist.index_map = index_map
        self.figure_canvas.draw()
    
    def __replot__(self):
        self.ax.cla()
        self.ax.yaxis.set_major_formatter('{x:.2e}')
        if self.log_x:
            self.ax.set_xscale('log')
        else:
            self.ax.set_xscale('linear')
        if self.log_y:
            self.ax.set_yscale('log')
        else:
            self.ax.set_yscale('linear')
            
        if self.temperature_dependent:
            self.ax.set_xlabel("Temperature [K]")
        else:
            self.ax.set_xlabel("Field [Oe]")
        if self.magnetisation_mode == "moment":
            if self.inverse:
                self.ax.set_ylabel("inverse magnetisation [1/emu]")
            else:
                self.ax.set_ylabel("magnetisation [emu]")
        elif self.magnetisation_mode == "moment mu bohr":
            if self.inverse:
                self.ax.set_ylabel("inverse magnetisation [f.u./$\mu_B$]")
            else:
                self.ax.set_ylabel("magnetisation [$\mu_B$/f.u.]")
        elif self.magnetisation_mode == "mass magnetisation":
            if self.inverse:
                self.ax.set_ylabel("inverse magnetisation [g/emu]")
            else:
                self.ax.set_ylabel("magnetisation [emu/g]")
        elif self.magnetisation_mode == "molar magnetisation":
            if self.inverse:
                self.ax.set_ylabel("inverse magnetisation [mol/emu]")
            else:
                self.ax.set_ylabel("magnetisation [emu/mol]")
        elif self.magnetisation_mode == "volume":
            if self.inverse:
                self.ax.set_ylabel("inverse susceptibility [cm^3/emu]")
            else:
                self.ax.set_ylabel("susceptibility [emu/cm^3]")
        elif self.magnetisation_mode == "mass":
            if self.inverse:
                self.ax.set_ylabel("inverse mass susceptibility [g/emu]")
            else:
                self.ax.set_ylabel("mass susceptibility [emu/g]")
        elif self.magnetisation_mode == "molar":
            if self.inverse:
                self.ax.set_ylabel("inverse molar susceptibility [mol/emu]")
            else:
                self.ax.set_ylabel("molar susceptibility [emu/mol]")
        
        for measurement, index_map, label in zip(self.measurements, self.index_maps, self.labels):
            self.plot_measurement_data(measurement, index_map, label)
        
        if self.labels != [''] * len(self.measurements):
            self.__init_legend__()
            self.figure_canvas.draw()
            
        for dialog in self.dialogs:
            for direction in ["tl", "tr", "bl", "br"]:
                dialog.draw_datapoint_on_parent(dialog.datapoints[direction],
                                                direction,
                                                dialog.indexes[direction],
                                                False)
                dialog.__plot_datapoint__(dialog.indexes[direction],
                                          direction)
        
    def actionClick(self, event):
        if event.artist.in_legend:
            handler = event.artist
            scatter = self.map_legend_to_scatter[handler]
            vis = not scatter.get_visible()
            scatter.set_visible(vis)
            handler.set_alpha(1.0 if vis else 0.2)
            self.figure_canvas.draw()
        elif event.mouseevent.dblclick:
            artist = event.artist
            index = artist.measurement.get_closest_datapoint_subset(event.mouseevent.xdata,
                                                                    event.mouseevent.ydata,
                                                                    artist.index_map,
                                                                    self.temperature_dependent,
                                                                    self.magnetisation_mode,
                                                                    self.center_mode,
                                                                    self.inverse,
                                                                    return_index=True)
            dialog = DatapointPlotDialog(self, artist.measurement, artist.index_map, index)
            self.dialogs.append(dialog)
            dialog.show()
        
    def __init_popup_menu__(self):
        self.popMenu = QMenu(self)
        
        self.moment_T_action = self.popMenu.addAction("M(T)")
        self.moment_T_action.setCheckable(True)
        self.moment_T_action.setChecked(True)
        self.moment_T_action.triggered.connect(self.plot_m_T)
        self.moment_H_action = self.popMenu.addAction("M(H)")
        self.moment_H_action.setCheckable(True)
        self.moment_H_action.triggered.connect(self.plot_m_H)
        action_group = QActionGroup(self)
        action_group.addAction(self.moment_T_action)
        action_group.addAction(self.moment_H_action)
        
        self.popMenu.addSeparator()
        
        self.free_center_action = self.popMenu.addAction("free center")
        self.free_center_action.setCheckable(True)
        self.free_center_action.setChecked(True)
        self.free_center_action.triggered.connect(self.plot_free_center)
        self.fixed_center_action = self.popMenu.addAction("fixed center")
        self.fixed_center_action.setCheckable(True)
        self.fixed_center_action.triggered.connect(self.plot_fixed_center)
        action_group = QActionGroup(self)
        action_group.addAction(self.free_center_action)
        action_group.addAction(self.fixed_center_action)
        
        self.popMenu.addSeparator()
        
        self.moment_action = self.popMenu.addAction("magnetisation")
        self.moment_action.setCheckable(True)
        self.moment_action.setChecked(True)
        self.moment_action.triggered.connect(self.plot_magnetic_moment)
        self.moment_mu_bohr_action = self.popMenu.addAction("magnetisation [\u03BC_B/f.u.]")
        self.moment_mu_bohr_action.setCheckable(True)
        self.moment_mu_bohr_action.triggered.connect(self.plot_moment_mu_bohr)
        #self.moment_action.setChecked(True)
        #self.moment_action.triggered.connect(self.plot_magnetic_moment)
        self.mass_magnetisation_action = self.popMenu.addAction("mass magnetisation")
        self.mass_magnetisation_action.setCheckable(True)
        self.mass_magnetisation_action.triggered.connect(self.plot_mass_magnetisation)
        self.molar_magnetisation_action = self.popMenu.addAction("molar magnetisation")
        self.molar_magnetisation_action.setCheckable(True)
        self.molar_magnetisation_action.triggered.connect(self.plot_molar_magnetisation)
        self.volume_x_action = self.popMenu.addAction("volume susceptibility")
        self.volume_x_action.triggered.connect(self.plot_volume_susceptibility)
        self.volume_x_action.setCheckable(True)
        self.mass_x_action = self.popMenu.addAction("mass susceptibility")
        self.mass_x_action.triggered.connect(self.plot_mass_susceptibility)
        self.mass_x_action.setCheckable(True)
        self.molar_x_action = self.popMenu.addAction("molar susceptibility")
        self.molar_x_action.triggered.connect(self.plot_molar_susceptibility)
        self.molar_x_action.setCheckable(True)
        self.action_dic = {"moment" : self.moment_action,
                           "mass magnetisation" : self.mass_magnetisation_action,
                           "molar magnetisation" : self.molar_magnetisation_action,
                           "volume" : self.volume_x_action,
                           "mass" : self.mass_x_action,
                           "molar" : self.molar_x_action}
        action_group = QActionGroup(self)
        action_group.addAction(self.moment_action)
        action_group.addAction(self.moment_mu_bohr_action)
        action_group.addAction(self.mass_magnetisation_action)
        action_group.addAction(self.molar_magnetisation_action)
        action_group.addAction(self.volume_x_action)
        action_group.addAction(self.mass_x_action)
        action_group.addAction(self.molar_x_action)
        
        self.popMenu.addSeparator()
        
        self.inverse_action = self.popMenu.addAction("inverse")
        self.inverse_action.setCheckable(True)
        self.inverse_action.triggered.connect(self.plot_inverse)
        action_group = QActionGroup(self)
        action_group.addAction(self.inverse_action)
        
        self.log_x_action = self.popMenu.addAction("log x-axis")
        self.log_x_action.setCheckable(True)
        self.log_x_action.triggered.connect(self.plot_log_x)
        action_group = QActionGroup(self)
        action_group.addAction(self.log_x_action)
        
        self.log_y_action = self.popMenu.addAction("log y-axis")
        self.log_y_action.setCheckable(True)
        self.log_y_action.triggered.connect(self.plot_log_y)
        action_group = QActionGroup(self)
        action_group.addAction(self.log_y_action)
        
        
        
    def plot_m_T(self, event):
        self.temperature_dependent = True
        self.__replot__()
        
    def plot_m_H(self, event):
        self.temperature_dependent = False
        self.__replot__()
        
    def plot_magnetic_moment(self, event):
        self.magnetisation_mode = "moment"
        self.__replot__()
        
    def plot_moment_mu_bohr(self, event):
        for measurement in self.measurements:
            if measurement.sample_rdf.sample_molar_mass is None:
                self.window()._console.append("> No molar mass is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
            if measurement.sample_rdf.sample_mass == "":
                self.window()._console.append("> No sample mass is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
        self.magnetisation_mode = "moment mu bohr"
        self.__replot__()
        
    def plot_mass_magnetisation(self, event):
        for measurement in self.measurements:
            if measurement.sample_rdf.sample_mass == "":
                self.window()._console.append("> No sample mass is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
        self.magnetisation_mode = "mass magnetisation"
        self.__replot__()
        
    def plot_molar_magnetisation(self, event):
        for measurement in self.measurements:
            if measurement.sample_rdf.sample_density is None:
                self.window()._console.append("> No density is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
            if measurement.sample_rdf.sample_mass == "":
                self.window()._console.append("> No sample mass is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
        self.magnetisation_mode = "molar magnetisation"
        self.__replot__()
        
    def plot_volume_susceptibility(self, event):
        for measurement in self.measurements:
            if measurement.sample_rdf.sample_density is None:
                self.window()._console.append("> No density is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
            if measurement.sample_rdf.sample_mass == "":
                self.window()._console.append("> No sample mass is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
        self.magnetisation_mode = "volume"
        self.__replot__()
        
    def plot_mass_susceptibility(self, event):
        for measurement in self.measurements:
            if measurement.sample_rdf.sample_mass == "":
                self.window()._console.append("> No sample mass is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
        self.magnetisation_mode = "mass"
        self.__replot__()
        
    def plot_molar_susceptibility(self, event):
        for measurement in self.measurements:
            if measurement.sample_rdf.sample_molar_mass is None:
                self.window()._console.append("> No molar mass is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
            if measurement.sample_rdf.sample_mass == "":
                self.window()._console.append("> No sample mass is specified in measurement '{}'".format(measurement.name))
                self.action_dic[self.magnetisation_mode].setChecked(True)
                return
        self.magnetisation_mode = "molar"
        self.__replot__()
        
    def plot_free_center(self, event):
        self.center_mode = "free"
        self.__replot__()
        
    def plot_fixed_center(self, event):
        self.center_mode = "fixed"
        self.__replot__()
        
    def plot_inverse(self, event):
        self.inverse = not self.inverse
        self.inverse_action.setChecked(self.inverse)
        self.__replot__()
    
    def plot_log_x(self, event):
        self.log_x = not self.log_x
        self.log_x_action.setChecked(self.log_x)
        if self.log_x:
            self.ax.set_xscale('log')
        else:
            self.ax.set_xscale('linear')
        self.figure_canvas.draw()
        
    def plot_log_y(self, event):
        self.log_y = not self.log_y
        self.log_y_action.setChecked(self.log_y)
        if self.log_y:
            self.ax.set_yscale('log')
        else:
            self.ax.set_yscale('linear')
        self.figure_canvas.draw()
    
    def actionClick2(self, event):
        if event.button == 3:
            cursor = QCursor()
            self.popMenu.popup(cursor.pos())
            