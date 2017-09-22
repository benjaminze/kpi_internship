# -*- coding: utf-8 -*-
"""
Created on Fri Sep 22 12:33:13 2017

This module creates text-files.
Input: filename, device_idn, table
"""
from PyQt4 import QtGui

class exportToTextfile(QtGui.QTableWidget):
    def __init__(self, filename, device_idn, table):
        self.filename   = filename
        self.idn        = device_idn
        self.table      = table
        
    def CreateString(self):
        QtGui.QTableWidget.ge
#       # create string to export
#        data_to_write    = [0 for i in range(int(sample_count)+2)]
#        data_to_write[0] = 'IDN: '+ self.idn
#        data_to_write[1] = 'All measurement data in [V]'      
#        
#        # print string to textbox
#        data_string = ''        
#        for item in data_to_write:
#            data_string += ('%s\n' %item)
#        self.measurement_data_textBox.setText(data_string)