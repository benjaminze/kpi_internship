# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 12:33:13 2017

This module creates text-files.
Input: filename, device_idn, table
"""
from PyQt4 import QtGui


class ExportToTextfile(QtGui.QTableWidget):
    def __init__(self, filename, device_idn, table):
        self.filename   = filename + '.txt'
        self.idn        = device_idn
        self.table      = table
        
    def WriteToFile(self):
  
        file = open(self.filename, 'w')

#        file.write( 'IDN: '+ self.idn + ' \n' 
 #       + 'All measurement data in [V]')
        
        row_count       = self.table.rowCount()
        coloumn_count   = self.table.coloumnCount()
        content         = ''
        for row in range(row_count):
            file.write('\n')            
            for coloumn in range(coloumn_count):
                content = self.table.item(row, coloumn)
                print(content)                
                #file.write(content + '    ')
                
                
        file.close()
        print('Data successfully saved to file')