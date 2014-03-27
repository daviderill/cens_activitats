# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'photo.ui'
#
# Created: Tue Feb 25 11:58:55 2014
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(686, 565)
        self.label_photo = QtGui.QLabel(Form)
        self.label_photo.setGeometry(QtCore.QRect(20, 10, 641, 481))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(9)
        font.setWeight(50)
        font.setBold(False)
        self.label_photo.setFont(font)
        self.label_photo.setAutoFillBackground(True)
        self.label_photo.setText(_fromUtf8(""))
        self.label_photo.setPixmap(QtGui.QPixmap(_fromUtf8("fotos/352.jpg")))
        self.label_photo.setAlignment(QtCore.Qt.AlignCenter)
        self.label_photo.setObjectName(_fromUtf8("label_photo"))
        self.label_info = QtGui.QLabel(Form)
        self.label_info.setGeometry(QtCore.QRect(90, 530, 181, 21))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Arial"))
        font.setPointSize(9)
        font.setWeight(50)
        font.setBold(False)
        self.label_info.setFont(font)
        self.label_info.setObjectName(_fromUtf8("label_info"))

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.label_info.setText(QtGui.QApplication.translate("Form", "Info", None, QtGui.QApplication.UnicodeUTF8))

