# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'traininglogswindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(640, 420)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.qpbox_training_logs = QtWidgets.QGroupBox(self.centralwidget)
        self.qpbox_training_logs.setGeometry(QtCore.QRect(10, 10, 621, 371))
        self.qpbox_training_logs.setObjectName("qpbox_training_logs")
        self.txt_training_logs = QtWidgets.QTextEdit(self.qpbox_training_logs)
        self.txt_training_logs.setGeometry(QtCore.QRect(0, 30, 620, 310))
        self.txt_training_logs.setReadOnly(True)
        self.txt_training_logs.setObjectName("txt_training_logs")
        self.btn_back_page = QtWidgets.QPushButton(self.centralwidget)
        self.btn_back_page.setGeometry(QtCore.QRect(270, 355, 100, 25))
        self.btn_back_page.setObjectName("btn_back_page")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        SrcSize = QtGui.QScreen.availableGeometry(QtWidgets.QApplication.primaryScreen())
        frmX = (SrcSize.width() - MainWindow.width())/2
        frmY = (SrcSize.height() - MainWindow.height())/2
        MainWindow.move(frmX, frmY)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Logs de Treinamento"))
        self.qpbox_training_logs.setTitle(_translate("MainWindow", "Logs de treinamento"))
        self.btn_back_page.setText(_translate("MainWindow", "Voltar"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
