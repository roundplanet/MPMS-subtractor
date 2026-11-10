## Overview

**MPMS Subtractor** is a software tool for performing background subtraction on DC scans acquired using Quantum Design MPMS3 or MPMS5 systems.

When measurements are available both with and without the sample mounted on the sample holder (or in a pressure cell or other measurement device), the software performs a point-by-point subtraction of the raw measurement scans. The resulting signal is then fitted with a new dipole function using the provided fitting parameters.

This approach determines the resulting magnetic moment directly from the background-subtracted signal, providing significantly more accurate results than simply subtracting the magnetic moments reported by Quantum Design's MultiVu software.

### Additional Features

- **Raw Data Subtraction:** Point-by-point subtraction of raw DC scan data from measurements with and without the sample.
- **Improved Moment Determination:** Refitting of the background-subtracted signal using a dipole function to obtain a more accurate magnetic moment.
- **He3 Data Support:** Processing of He3 measurements, including conversion of the original data into a compatible format directly within the software.
- **Missing Data Point Reconstruction:** Recovery of missing measurement points caused by signal acquisition errors, provided that the corresponding `.scans.rw.dat` file has also been generated.

The software is designed to improve the accuracy and reliability of magnetic moment measurements, particularly when background contributions from sample holders, pressure cells, or other measurement devices are significant.

### Contact

For further information, questions, or support, please contact:

julian.kaiser@uni-a.de