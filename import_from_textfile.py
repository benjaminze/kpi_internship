# -*- coding: utf-8 -*-
"""This module imports data from existing textfile that was created by this program

Inputs: file, QTableWidget
returns device_idn
"""

from PyQt4 import QtGui

class ImportFromTextfile(QtGui.QTableWidget):
    def __init__(self, file, table):
        self.file       = file
        self.table      = table
    
    
    def ImportData(self):
         # split text in lines
        textlines       = self.file.read().splitlines()
        
        # clear table and set columnCount
        self.table.    setRowCount(0)
        self.table.    setColumnCount(4)
        
        # enable horzontal header and hide vertical header
        self.table.verticalHeader().   setVisible(False)
        self.table.horizontalHeader(). setVisible(True )
        
        # write header to table
        headers = textlines[2].split()
        for i,header in enumerate(headers):
            self.table.setHorizontalHeaderItem(i, QtGui.QTableWidgetItem(header))
        
        # split lines in columns
        for line in textlines[3:]:
            current_line = line.split()            
            
            row_count = self.table.rowCount()
            self.table.insertRow(row_count)
            
            self.table.setItem(row_count, 0, QtGui.QTableWidgetItem(current_line[0]))
            self.table.setItem(row_count, 1, QtGui.QTableWidgetItem('{} {}'.format(current_line[1],current_line[2])))
            self.table.setItem(row_count, 2, QtGui.QTableWidgetItem(current_line[3]))
            self.table.setItem(row_count, 3, QtGui.QTableWidgetItem(current_line[4]))
            
#            self.table.scrollToBottom()
        
        self.table.resizeColumnsToContents()   
        
        device_idn = textlines[0].split()[1]
        
        return device_idn