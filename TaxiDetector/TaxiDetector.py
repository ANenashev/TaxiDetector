#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
import os
import VideoProcessing as vp
 
class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Taxi detector'
        self.left = 50
        self.top = 50
        self.width = 640
        self.height = 110        
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        self.fOpenTextbox = QLineEdit(self)
        self.fOpenTextbox.move(20, 20)
        self.fOpenTextbox.resize(500,20)

        self.fSaveTextbox = QLineEdit(self)
        self.fSaveTextbox.move(20, 50)
        self.fSaveTextbox.resize(500,20)        
 

        self.btnOpen = QPushButton('Open source', self)
        self.btnOpen.move(520,18)
        
        self.btnSave = QPushButton('Save', self)
        self.btnSave.move(520,46)

        self.btnProcess = QPushButton('Process video file', self)
        self.btnProcess.move(260, 80)
        

        self.btnOpen.clicked.connect(self.on_btnOpen_click)
        self.btnSave.clicked.connect(self.on_btnSave_click)
        self.btnProcess.clicked.connect(self.on_btnProcess_click)

 
        self.show()

    def openFileDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Open source video", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            return(fileName)
        else:
            return(None)

    def saveFileDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self,"Save to","","All Files (*);;Text Files (*.txt)", options=options)
        if fileName:
            return(fileName)
        else:
            return(None)

    @pyqtSlot()
    def on_btnOpen_click(self):
        textboxValue = self.openFileDialog()
        if (textboxValue is not None):
            self.fOpenTextbox.setText(textboxValue)
        else:
            self.fOpenTextbox.setText("")

    @pyqtSlot()
    def on_btnSave_click(self):
        textboxValue = self.saveFileDialog()
        if (textboxValue is not None):
            self.fSaveTextbox.setText(textboxValue)
        else:
            self.fSaveTextbox.setText("")

    @pyqtSlot()
    def on_btnProcess_click(self):
        #Проверяем, выбран ли файл
        source = self.fOpenTextbox.text()
        if (source == ""):
            QMessageBox.information(self, "Warning","Choose source video file!", QMessageBox.Yes)
            return
        elif (not os.path.exists(source)):
            QMessageBox.information(self, "Warning","File doesn't exist!", QMessageBox.Yes)            
            return        

        dest = self.fSaveTextbox.text()

        #Если имя выходного файла не выбрано, придумаем его самостоятельно
        if (dest == ""):
            dest_dir = os.path.dirname(source)
            dest_file = os.path.split(source)[1]
            dest_name, dest_ext = dest_file.split('.')
            dest_name += "_processed"+'.'+dest_ext
            dest = os.path.join(os.path.abspath(dest_dir),dest_name)
            self.fSaveTextbox.setText(dest)

        vp.ProcessVideo(self.fOpenTextbox.text(), self.fSaveTextbox.text())

 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())