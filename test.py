# -*- coding: utf-8 -*-
"""
Created on Mon May 12 13:52:23 2025

@author: kaisjuli
"""

"""
from data import RawDataFile
from calculation import fit_signal, gradiometer_function

rdf = RawDataFile("C:/Users/kaisjuli/Downloads/M20171121_Pd_one_torlon_M(T)_at_10000_Oe.rw.dat")
for rdp in rdf.datapoints:
    print(rdp.temperature)
    
rdf.print_sample_info()
print(len(rdf.datapoints))
pos = 0
res = fit_signal(rdf.datapoints[pos].raw_position, rdf.datapoints[pos].processed_voltage)
print(res)

import matplotlib.pyplot as plt
import numpy as np

plt.figure()
plt.scatter(rdf.datapoints[pos].raw_position, rdf.datapoints[pos].processed_voltage)

x = np.linspace(np.min(rdf.datapoints[pos].raw_position), np.max(rdf.datapoints[pos].raw_position), 1000)
plt.scatter(x, gradiometer_function(x, *res[0]))

print(np.max(gradiometer_function(x, *res[0])) - np.min(gradiometer_function(x, *res[0])))

magnetization_factor = -0.00285897 * 14.7029 * rdf.datapoints[pos].squid_range / 1000
magnetization = magnetization_factor * res[0][-1]
print(magnetization)

fitted_data = np.loadtxt("../test_area/test_data_fitted.txt")
plt.scatter(fitted_data[:, 1], fitted_data[:, 3], s=2, label="fit")

x = np.linspace(20, 60, 1000)
plt.scatter(x, np.polynomial.Polynomial.fit(fitted_data[:, 1], fitted_data[:, 3], 10)(x), s=2)

"""

from src.data import RawDataFile, Measurement
from src.calculation import fit_signal, gradiometer_function, subtract_background

sample = RawDataFile("C:/Users/kaisjuli/Downloads/M20171121_Pd_one_torlon_M(T)_at_10000_Oe.rw.dat")
bg = RawDataFile("C:/Users/kaisjuli/Downloads/M20171121_Pd_one_torlon_M(T)_at_10000_Oe_background.rw.dat")

import matplotlib.pyplot as plt
import numpy as np

pos = 0

plt.figure()
plt.scatter(sample.datapoints[pos].raw_position, sample.datapoints[pos].processed_voltage, s=2)
plt.scatter(bg.datapoints[pos].raw_position, bg.datapoints[pos].processed_voltage, s=2)

#(len(sample.datapoints[pos].raw_position), len(bg.datapoints[pos].raw_position))

x_min = max([np.min(sample.datapoints[pos].raw_position), np.min(bg.datapoints[pos].raw_position)])
x_max = min([np.max(sample.datapoints[pos].raw_position), np.max(bg.datapoints[pos].raw_position)])

x = np.linspace(x_min, x_max, len(sample.datapoints[pos].raw_position))

y_sample = np.interp(x, sample.datapoints[pos].raw_position, sample.datapoints[pos].processed_voltage)
y_bg = np.interp(x, bg.datapoints[pos].raw_position, bg.datapoints[pos].processed_voltage)

plt.scatter(x, y_sample, s=2)
plt.scatter(x, y_bg, s=2)

plt.figure()
plt.scatter(x, y_sample, s=2)

res = fit_signal(x, y_sample-y_bg)
res = fit_signal(sample.datapoints[pos].raw_position, sample.datapoints[pos].processed_voltage, None, False)
print(res)
print(res[0][0] * -0.00285897 * 14.7029 / 1000)
#print(np.sqrt(np.diag(res[0]))[0] * 0.00285897 * 14.7029 / 1000)
plt.scatter(x, gradiometer_function(x, *res[0]), s=2, label="hier")
plt.legend()


temps = []
amplitudes = []
for s, b in zip(sample.datapoints, bg.datapoints):
    x, y = subtract_background(s, b)
    res = fit_signal(x, y)
    temps.append(s.temperature)
    amplitudes.append(res[0][0])
    
plt.figure()
plt.scatter(s.raw_position, s.processed_voltage, label="sample")
plt.scatter(b.raw_position, b.processed_voltage, label="bg")
plt.scatter(x, y, label="diff")
plt.scatter(x, gradiometer_function(x, *res[0]), label="fit")
plt.legend()
    
plt.figure()
plt.scatter(temps, amplitudes)

plt.figure()
m = Measurement("C:/Users/kaisjuli/Downloads/M20171121_Pd_one_torlon_M(T)_at_10000_Oe.rw.dat",
                "C:/Users/kaisjuli/Downloads/M20171121_Pd_one_torlon_M(T)_at_10000_Oe_background.rw.dat")
temps = []
amplitudes = []
for dp in m:
    temps.append(dp.sample_rdp.temperature)
    amplitudes.append(dp.datapoint_result["moment"])# * 2.7287179487179487e4)
plt.scatter(temps, amplitudes)

plt.figure()
temps = []
amplitudes = []
for dp in m:
    temps.append(dp.sample_rdp.temperature)
    amplitudes.append(dp.sample_result["moment"])# * 2.7287179487179487e4)
plt.scatter(temps, amplitudes)

plt.figure()
temps = []
amplitudes = []
for dp in m:
    temps.append(dp.sample_rdp.temperature)
    amplitudes.append(dp.background_result["moment"])# * 2.7287179487179487e4)
plt.scatter(temps, amplitudes)

plt.figure()
for dp in m:
    plt.scatter(dp.sample_rdp.raw_position, dp.sample_rdp.processed_voltage, s=2)
    plt.scatter(dp.sample_rdp.raw_position, gradiometer_function(dp.sample_rdp.raw_position, *dp.sample_result["fit_coeff"]))
    break