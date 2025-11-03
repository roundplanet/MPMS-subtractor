# -*- coding: utf-8 -*-
"""
Created on Wed May 14 15:38:54 2025

@author: kaisjuli
"""

import sys
from PyQt5.QtWidgets import QApplication

from src.gui.main_window import MainWindow

app = QApplication(sys.argv)
Window = MainWindow()
Window.show()
sys.exit(app.exec())