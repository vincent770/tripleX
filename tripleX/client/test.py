#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from communication import mysocket
import threading
from myThreading import MyThread #重写的线程类
import time
from queue import Queue
import pyperclip

from PyQt5.QtWidgets import QApplication
import PyQt5.QtCore as QtCore
from qttray import Window_tray

import sys
import os
app = QApplication(sys.argv)
cb = QApplication.clipboard()



print(cb.mimeData().text() )


cb.setText("I've been clipped!")

files = ['/Users/vt/Desktop/copyto/wonderbits','/Users/vt/Desktop/copyto/test.py']
data = QtCore.QMimeData()
url = [QtCore.QUrl.fromLocalFile(file) for file in files]
data.setUrls(url)
app.clipboard().setMimeData(data)

sys.exit(app.exec())

