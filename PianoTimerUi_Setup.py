# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PianoTimerUi_Setup.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_DialogSetup(object):
    def setupUi(self, DialogSetup):
        DialogSetup.setObjectName(_fromUtf8("DialogSetup"))
        DialogSetup.resize(315, 200)
        DialogSetup.setMinimumSize(QtCore.QSize(315, 200))
        DialogSetup.setMaximumSize(QtCore.QSize(315, 200))
        self.formLayout = QtGui.QFormLayout(DialogSetup)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(DialogSetup)
        self.label.setMinimumSize(QtCore.QSize(100, 30))
        self.label.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Noto Sans [unknown]"))
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.comboBox_Method = QtGui.QComboBox(DialogSetup)
        self.comboBox_Method.setMinimumSize(QtCore.QSize(180, 32))
        self.comboBox_Method.setMaximumSize(QtCore.QSize(180, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Noto Sans [unknown]"))
        font.setPointSize(11)
        self.comboBox_Method.setFont(font)
        self.comboBox_Method.setObjectName(_fromUtf8("comboBox_Method"))
        self.comboBox_Method.addItem(_fromUtf8(""))
        self.comboBox_Method.addItem(_fromUtf8(""))
        self.comboBox_Method.addItem(_fromUtf8(""))
        self.horizontalLayout_2.addWidget(self.comboBox_Method)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label_2 = QtGui.QLabel(DialogSetup)
        self.label_2.setMinimumSize(QtCore.QSize(100, 30))
        self.label_2.setMaximumSize(QtCore.QSize(100, 30))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Noto Sans [unknown]"))
        font.setPointSize(11)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.horizontalLayout.addWidget(self.label_2)
        self.comboBox_SaveWav = QtGui.QComboBox(DialogSetup)
        self.comboBox_SaveWav.setMinimumSize(QtCore.QSize(180, 32))
        self.comboBox_SaveWav.setMaximumSize(QtCore.QSize(180, 32))
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Noto Sans [unknown]"))
        font.setPointSize(11)
        self.comboBox_SaveWav.setFont(font)
        self.comboBox_SaveWav.setObjectName(_fromUtf8("comboBox_SaveWav"))
        self.comboBox_SaveWav.addItem(_fromUtf8(""))
        self.comboBox_SaveWav.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.comboBox_SaveWav)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.formLayout.setLayout(0, QtGui.QFormLayout.LabelRole, self.verticalLayout)

        self.retranslateUi(DialogSetup)
        QtCore.QMetaObject.connectSlotsByName(DialogSetup)

    def retranslateUi(self, DialogSetup):
        DialogSetup.setWindowTitle(_translate("DialogSetup", "Performance", None))
        self.label.setText(_translate("DialogSetup", "Method", None))
        self.comboBox_Method.setItemText(0, _translate("DialogSetup", "Standard Frequency", None))
        self.comboBox_Method.setItemText(1, _translate("DialogSetup", "Recorded Frquency", None))
        self.comboBox_Method.setItemText(2, _translate("DialogSetup", "Cross Correlation", None))
        self.label_2.setText(_translate("DialogSetup", "Save Wav File", None))
        self.comboBox_SaveWav.setItemText(0, _translate("DialogSetup", "No", None))
        self.comboBox_SaveWav.setItemText(1, _translate("DialogSetup", "Yes", None))
