# -*- coding: utf-8 -*-
from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_photo import Ui_Form


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class PhotoDialog(QtGui.QDialog):

    def __init__(self):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_Form()
        self.ui.setupUi(self)		

    def setPhoto(self, path):
        self.ui.label_info.setText("")
        self.ui.label_photo.setPixmap(QtGui.QPixmap(_fromUtf8(path)))		

    def setHeader(self, table, col, text):
        header = QtGui.QTableWidgetItem(text)
        table.setHorizontalHeaderItem(col, header)		