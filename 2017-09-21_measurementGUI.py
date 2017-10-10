import sys
from PyQt4 import QtCore, QtGui, uic
import datetime
import visa
import re

import numpy as np


import pyqtgraph as pg

from plot_data import PlotData
from import_from_textfile import ImportFromTextfile
from export_to_textfile import ExportToTextfile


qtCreatorFile = "measureGUI.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        # declare attributes for measurement     
        self.rm                     = None
        self.resources              = []
        self.instrument             = None
        self.integration_time       = 0
        self.idn                    = ''
        self.integration_time_list  = ['0.4',  '4','20', '40','200', '400','2000', '4000']
        self.nplc_list              = ['0.02','.2','1',  '2',  '10',  '20', '100',  '200'] 
        self.sample_count           = 1
        
        
        # declare attributes for data table     
        self.digits_sample_count    = 0
        self.nr_string              = ''
        self.channel                = 0
        
        # declare attributes for timer 
        self.timer_counter          = 0
        self.offset                 = 200 #[ms]
        self.timer                  = QtCore.QTimer(self)
        self.timer.setInterval(     self.offset)
        self.timer.timeout.connect( self.TimerMeasurement)
        
        # declare attributes for export    
        self.filename               = ''
        self.filename_lineEdit.setText('myData')
        
        # declare attributes for Plot
        self.plot_widget            = None
                       

        
        # Disable all possible actions except scan_instruments_button
        self.idn_button.                setEnabled(False)
        self.instruments_comboBox.      setEnabled(False)
        self.integration_time_comboBox. setEnabled(False)
        self.start_measurement_button.  setEnabled(False)
        self.stop_measurement_button.   setEnabled(False)
        self.export_data_button.        setEnabled(False)
        self.channel_1_checkBox.        setEnabled(False)
        self.channel_2_checkBox.        setEnabled(False)
        self.nr_of_measurements_spinBox.setEnabled(False)
        self.data_saved_lineEdit.       setEnabled(False)
        self.idn_textBox.               setEnabled(False)
#        self.plot_data_button.          setEnabled(False)
        
    def Main(self):
        '''Main function contains of all interactive Objects of the GUI.

        If buttens are pressed it connects these events with associated functions.
        '''
        

        # trigger scan for instruments
        self.scan_instruments_button.clicked.       connect(self.ScanForInstruments )
        self.scan_instruments_button.clicked.       connect(self.SetDefaultValues   )
        
        # import_data_button
        self.import_data_button.clicked.            connect(self.ImportData         )        
        
        # trigger get idn 
        self.idn_button.clicked.                    connect(self.GetIDN             )
        
        # monitor instruments_comboBox
        self.instruments_comboBox.activated.        connect(self.GetInstrument      )
        
        # monitor integration_time_comboBox
        self.integration_time_comboBox.activated.   connect(self.GetIntegrationTime )
        
        # trigger measurement start 
        self.start_measurement_button.clicked.      connect(self.StartMeasurement   )
        
        # stop measurement  
        self.stop_measurement_button.clicked.       connect(self.StopMeasurement    )
        
        # plot data        
#        self.plot_data_button.clicked.              connect(self.CreatePlotWidget   )
#        if self.plot_widget:        
#            self.measurement_data_table.cellChanged.connect(self.PlotData)
#        QtGui.QTableWidget.cellChanged.connect(self.PlotData)
        # export_data_button
        self.export_data_button.clicked.            connect(self.ExportToFile       )
        
        
    def ScanForInstruments(self):
        
        # enable buttons for next step        
        self.idn_button.            setEnabled(True)
        self.instruments_comboBox.  setEnabled(True)
        
        # clear idn_textBox        
        self.idn_textBox.clear()
        
        # get invertet list of connected resources
        self.rm         = visa.ResourceManager()        
        self.resources  = self.rm.list_resources()[::-1]

        # write lit of resources to instruments_comboBox
        self.instruments_comboBox.clear()
        self.instruments_comboBox.addItems(self.resources)
        
        
    def SetDefaultValues(self):      
        
        # Add itmes to integration_time_comboBox
        self.integration_time_comboBox.clear()
        self.integration_time_comboBox.addItems(self.integration_time_list)

        # Set default values
        self.instrument         = self.rm.open_resource(self.resources[0])
        self.integration_time   = eval(self.integration_time_list[0])


    def GetInstrument(self, index):
        
        # chosen instrument has changed
        self.idn_textBox.clear()
        self.instrument = self.rm.open_resource(self.instruments_comboBox.currentText())


    def GetIDN(self):
        
        # enable buttons for next step
        self.integration_time_comboBox. setEnabled(True)
        self.channel_1_checkBox.        setEnabled(True)
        self.channel_2_checkBox.        setEnabled(True)
        self.nr_of_measurements_spinBox.setEnabled(True)
        self.start_measurement_button.  setEnabled(True)
        self.idn_textBox.               setEnabled(True)
        
         # Get and print instruments IDN      
        self.idn = self.instrument.query('*IDN?')
        self.idn_textBox.setText(self.idn)


    def GetIntegrationTime(self, index):
        
        # chosen integration_time has changed
        self.integration_time = int(self.integration_time_comboBox.currentText())
        
        
    def GetChannel(self):

        # check which channels are chosen and return      
        if self.channel_1_checkBox.isChecked() and self.channel_2_checkBox.isChecked():
            channel = 12
        elif self.channel_1_checkBox.isChecked():
            channel = 1
        elif self.channel_2_checkBox.isChecked():
            channel = 2
        else:
            QtGui.QMessageBox.question(self, 'No channel selected',
            "No measurement channel chosen. \nPlease check at least one.", 
            QtGui.QMessageBox.Ok)  
            channel = None
        
        return channel
 
 
#%% Measurement        
    def StartMeasurement(self):
        '''This function gets all needed data for measurement, initializes instrument and QTableWidget.
        Then timer is started to trigger measurement.        
        '''
        # enable stop_measurement_button        
        self.stop_measurement_button.   setEnabled(True)
        
        # disable all actions        
        self.data_saved_lineEdit.       clear()        
        self.data_saved_lineEdit.       setEnabled(False)            
        self.export_data_button.        setEnabled(False)
        self.idn_button.                setEnabled(False)
        self.instruments_comboBox.      setEnabled(False)
        self.integration_time_comboBox. setEnabled(False)
        self.start_measurement_button.  setEnabled(False)
        self.scan_instruments_button.   setEnabled(False)
        self.channel_1_checkBox.        setEnabled(False)
        self.channel_2_checkBox.        setEnabled(False)
        self.nr_of_measurements_spinBox.setEnabled(False)
        self.idn_textBox.               setEnabled(False)
        self.import_data_button.        setEnabled(False)
#        self.plot_data_button.          setEnabled(False) 
        
        # initialize table attributes
        self.measurement_data_table.    setRowCount(0)
        self.timer_counter = 0
        self.timer.setInterval(self.offset)
        
        # create plot widget
        self.plot_widget = PlotData()
#        self.plot_widget.plot([0],[0])
#        self.plot_widget.plot(range(100), [i*i for i in range(100)])
#        self.plot_widget.plot(range(100),[i for i in range(100)])
        # get measurement parameters 
        self.channel                = self.GetChannel()
        if self.channel == None: 
            self.StopMeasurement(); return     # Stop function if no channel selected
        nplc_index                  = self.integration_time_comboBox.currentIndex()
        nplc                        = self.nplc_list[nplc_index] 
        self.sample_count           = self.nr_of_measurements_spinBox.value()     
        self.digits_sample_count    = len(str(self.sample_count))
        self.nr_string              = '{}{}{}'.format('{:', str(self.digits_sample_count), '}')
        
        

        # write channel to instrument if only one is chosen
        if not self.channel == 12:
            self.instrument.write('ROUT:TERM FRON%d'       % self.channel)
        
        # write nplc (corresponding to integration_time) to instrument
        self.instrument.write('SENS:VOLT:DC:NPLC %s'   % nplc)    
        
        # calculate timer offset
        if self.integration_time >= 200: self.offset = int(self.integration_time*2) # NEEDS CHANGE  
         
        # set timeout        
        self.instrument.timeout = int(self.integration_time  + self.offset*0.9)

        # create table
        self.measurement_data_table.setColumnCount(4)

        self.measurement_data_table.verticalHeader().   setVisible(False)
        self.measurement_data_table.horizontalHeader(). setVisible(True )
        self.measurement_data_table.setHorizontalHeaderItem(0, QtGui.QTableWidgetItem('Nr.'))
        self.measurement_data_table.setHorizontalHeaderItem(1, QtGui.QTableWidgetItem('Date'))
        self.measurement_data_table.setHorizontalHeaderItem(2, QtGui.QTableWidgetItem('Data_on_Ch_1_[V]'))
        self.measurement_data_table.setHorizontalHeaderItem(3, QtGui.QTableWidgetItem('Data_on_Ch_2_[V]'))

        # Start Measurement, it will be stopped in fct TimerMeasurement or StopMeasurement
        self.timer.start()
        
    
    def TimerMeasurement(self):
        '''Triggers measuremnt on desired channel(s) and writes Data dynamically to QTableWidget.
        
        Therefor it makes use of timer function. When enough data points are measured, 
        function wil stop measurement and enable all GUI-interactions.
        '''
        # Either two channels are chosen or only one
        if self.channel == 12:
            # Set timer interval: Must be bigger than device timeout
            self.timer.setInterval(2*(self.integration_time + self.offset))
            
            measurement_data = ['','']            
            
            # Query 'read' for first channel, device measures
            current_channel     = 1
            self.instrument.write('ROUT:TERM FRON%d' % current_channel)
            measurement_data[0] = self.instrument.query('READ?')[:-1] 
            
            # Query 'read' for second channel, device measures
            current_channel     = 2
            self.instrument.write('ROUT:TERM FRON%d' % current_channel)
            measurement_data[1] = self.instrument.query('READ?')[:-1]
            
            # Write data to table
            self.WriteToTableWidget(measurement_data)
            
            
        else:
            # Set timer interval: Must be bigger than device timeout
            self.timer.setInterval(self.integration_time + self.offset)
            
            # Query 'read', device measures
            measurement_data    = self.instrument.query('READ?')[:-1]
            self.WriteToTableWidget(measurement_data)

        # rescale column width
        self.measurement_data_table.resizeColumnsToContents()        
        
        # increase counter
        self.timer_counter += 1        
        
        # stop measurement if enough data points
        if self.sample_count == self.timer_counter:
            self.StopMeasurement()


    def WriteToTableWidget(self, measurement_data):
        '''Nr. of measurement, Date and Time, and given measurement data will 
        be written to QTableWidget to the associated column.
        
        '''
        # insert new line
        row_count = self.measurement_data_table.rowCount()
        self.measurement_data_table.insertRow(row_count)

        # write Nr and Time
        measurement_time    = str(datetime.datetime.now())[:-7]
        measurement_nr      = str(self.timer_counter + 1)
        self.measurement_data_table.setItem(row_count, 0, QtGui.QTableWidgetItem(self.nr_string.format(measurement_nr)))
        self.measurement_data_table.setItem(row_count, 1, QtGui.QTableWidgetItem(measurement_time))
        
#        nr_to_plot          = [int(measurement_nr)]
#        data_to_plot        = [0,0]
        # scroll to bottom
        self.measurement_data_table.scrollToBottom()
       
        # Write data to every column
        if self.channel == 1:
            self.measurement_data_table.setItem(row_count, 2, QtGui.QTableWidgetItem(measurement_data))
            self.measurement_data_table.setItem(row_count, 3, QtGui.QTableWidgetItem('-'))
#            data_to_plot[0] = measurement_data
#            data_to_plot[1] = 0
#            self.plot_widget.SetDataPoints(measurement_nr, measurement_data, channel=1)
#            self.PlotData(measurement_nr, measurement_data, channel=1)
        elif self.channel == 2:
            self.measurement_data_table.setItem(row_count, 2, QtGui.QTableWidgetItem('-'))
            self.measurement_data_table.setItem(row_count, 3, QtGui.QTableWidgetItem(measurement_data))
#            data_to_plot[0] = 0
#            data_to_plot[1] = measurement_data
#            self.PlotData(measurement_nr, measurement_data, channel=2)
#            self.plot_widget.SetDataPoints(measurement_nr, measurement_data, channel=2)
        else:
            self.measurement_data_table.setItem(row_count, 2, QtGui.QTableWidgetItem(measurement_data[0]))
            self.measurement_data_table.setItem(row_count, 3, QtGui.QTableWidgetItem(measurement_data[1]))
#            data_to_plot[0] = measurement_data[0]
#            data_to_plot[1] = measurement_data[1]     
#            self.PlotData(measurement_nr, measurement_data)
#            self.plot_widget.SetDataPoints(measurement_nr, measurement_data)
            
        # plot data
        self.plot_widget.SetDataPoints(measurement_nr, measurement_data, channel = self.channel)
        
#        self.plot_widget.plot(nr_to_plot,[float(data_to_plot[0])], symbol = 'o')
#        self.plot_widget.plot(nr_to_plot,[float(data_to_plot[1])], symbol = 'x')
        
    def StopMeasurement(self):
        
        # Enable all actions except stop_measurement_button            
        self.stop_measurement_button.   setEnabled(False)
        self.export_data_button.        setEnabled(True)
        self.idn_button.                setEnabled(True)
        self.instruments_comboBox.      setEnabled(True)
        self.integration_time_comboBox. setEnabled(True)
        self.start_measurement_button.  setEnabled(True)
        self.scan_instruments_button.   setEnabled(True)
        self.channel_1_checkBox.        setEnabled(True)
        self.channel_2_checkBox.        setEnabled(True)
        self.nr_of_measurements_spinBox.setEnabled(True)        
        self.idn_textBox.               setEnabled(True)
        self.import_data_button.        setEnabled(True)
#        self.plot_data_button.          setEnabled(True)
        
        # stop measurement
        self.timer.stop()


#%% IMPORT
    def ImportData(self):
        self.export_data_button.        setEnabled(False)
        
        # choose file and open
        openFile        = QtGui.QAction("&Open File", self)
        openFile.setStatusTip('Open File')
        openFilename    = QtGui.QFileDialog.getOpenFileName(self,'Open File')
        file            = open(openFilename, 'r')
        
        # create PlotWidget
        self.plot_widget = PlotData()
        
        # import data from file
        importFile      = ImportFromTextfile(file, self.measurement_data_table)
        device_idn      = importFile.ImportData(self.plot_widget)
        
        # write idn
        self.idn_textBox.               setEnabled(True)
        self.idn_textBox.setText(device_idn)

        # enable plot_data_button
#        self.plot_data_button.          setEnabled(True)   

#%% PLOT DATA
#    def CreatePlotWidget(self):
#        self.plot_widget = pg.PlotWidget()
#        self.plot_widget.show()        
##        self.PlotData()        
#        
#    def PlotData(self, nr, data_to_plot, channel=None, time=None):
#        
#        nr = [int(nr)]        
#        symbol_channel_1 = 'o'
#        symbol_channel_2 = 'x'
#        
#        # check if both channels were used
#        if channel == 1:
#            self.plot_widget.plot(nr,[float(data_to_plot)],     symbol = symbol_channel_1)
#        elif channel == 2:
#            self.plot_widget.plot(nr,[float(data_to_plot)],     symbol = symbol_channel_2)
#        else:
#            self.plot_widget.plot(nr,[float(data_to_plot[0])],  symbol = symbol_channel_1)
#            self.plot_widget.plot(nr,[float(data_to_plot[1])],  symbol = symbol_channel_2)
        
       
#%% Export
    def ExportToFile(self):
        
        # Get filename from lineEdit
        self.filename   = self.filename_lineEdit.text()
        
        # Write to file        
        textfile        = ExportToTextfile(self.filename, self.idn, self.measurement_data_table)
        success         = textfile.WriteToFile()
        
        # write message to lineEdit
        self.data_saved_lineEdit.setEnabled(True)
        self.data_saved_lineEdit.setReadOnly(False)        
        self.data_saved_lineEdit.setText(success)
        self.data_saved_lineEdit.setReadOnly(True)

#%% CLOSE        
    def closeEvent(self, event):
        
        # Ask for confirmation
        reply = QtGui.QMessageBox.question(self, 'Quit?',
            "Are you sure to quit? \nAll Windows will be closed.", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        
        # Quit or stay
        if reply == QtGui.QMessageBox.Yes:
            # stop measurement if still running
            self.StopMeasurement()            
            
            # Set instrumets values to default            
            self.instrument.write("*RST")
            
            # close plot
            self.plot_widget.close()
            
            event.accept()
        else:
            event.ignore()   
            

#%% main
if __name__ == "__main__":
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.Main()
    window.show()
sys.exit(app.exec_())
