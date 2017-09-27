import sys
from PyQt4 import QtCore, QtGui, uic
import datetime
import visa
from export_to_textfile import ExportToTextfile


qtCreatorFile = "measureGUI.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        # declare attributes     
        self.rm                     = None
        self.resources              = []
        self.instrument             = None
        self.lib                    = None
        self.integration_time       = 0
        self.idn                    = ''
        self.integration_time_list  = ['0.4',  '4','20', '40','200', '400','2000', '4000']
        self.nplc_list              = ['0.02','.2','1',  '2',  '10',  '20', '100',  '200'] 
        self.sample_count           = 1
        self.filename               = ''
        self.digits_sample_count    = 0
        self.nr_string              = ''
        self.channel                = 0

        self.filename_lineEdit.setText('myData')
                       
        
        # timer 
        self.timer_counter          = 0
        self.offset                 = 200 #[ms]
        self.timer                  = QtCore.QTimer(self)
        self.timer.setInterval(self.offset)
        self.timer.timeout.connect(self.TimerMeasurement)
	# use viWaitonEvent maybe like that: visa.viWaitOnEvent()
	# or create an Event when status bit has flipped
        
        # Disable all Buttons and so on
#        self.scan_instruments_button.setEnabled(True)
        self.idn_button.setEnabled(False)
        self.instruments_comboBox.setEnabled(False)
        self.integration_time_comboBox.setEnabled(False)
        self.start_measurement_button.setEnabled(False)
        self.stop_measurement_button.setEnabled(False)
        self.export_data_button.setEnabled(False)
        self.channel_1_checkBox.setEnabled(False)
        self.channel_2_checkBox.setEnabled(False)
        self.nr_of_measurements_spinBox.setEnabled(False)
        self.data_saved_lineEdit.setEnabled(False)
        self.idn_textBox.setEnabled(False)
        
    def Main(self):
        '''Important information about this function

 
        '''
        

        #Trigger scan for instruments
        self.scan_instruments_button.clicked.connect(self.ScanForInstruments)
        self.scan_instruments_button.clicked.connect(self.SetDefaultValues)
        
        # trigger get idn 
        self.idn_button.clicked.connect(self.GetIDN)
        
        # monitor instruments_comboBox
        self.instruments_comboBox.activated.connect(self.GetInstrument)
        
        # monitor integration_time_comboBox
        self.integration_time_comboBox.activated.connect(self.GetIntegrationTime)
        
        # trigger measurement start 
        self.start_measurement_button.clicked.connect(self.StartMeasurement)
        
        # stop measurement  
        self.stop_measurement_button.clicked.connect(self.StopMeasurement)
        
        # export_data_button
        self.export_data_button.clicked.connect(self.ExportToFile)
        
        
    def ScanForInstruments(self):
        self.idn_button.setEnabled(True)
        self.instruments_comboBox.setEnabled(True)
        # get invertet list of connected resources
        self.rm         = visa.ResourceManager()        
        self.resources  = self.rm.list_resources()[::-1]

        
        # write data to instruments_comboBox
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
        self.idn_textBox.TextEdit.clear()
        self.instrument = self.rm.open_resource(self.instruments_comboBox.currentText())


    def GetIDN(self):
        self.integration_time_comboBox.setEnabled(True)
        self.channel_1_checkBox.setEnabled(True)
        self.channel_2_checkBox.setEnabled(True)
        self.nr_of_measurements_spinBox.setEnabled(True)
        self.start_measurement_button.setEnabled(True)
        self.idn_textBox.setEnabled(True)
        
         # Get instruments IDN and print in idn_textBox        
        self.idn = self.instrument.query('*IDN?')
        self.idn_textBox.setText(self.idn)


    def GetIntegrationTime(self, index):
        # chosen channel has changed
        self.integration_time = int(self.integration_time_comboBox.currentText())
        
        
    def GetChannel(self):
        
        if self.channel_1_checkBox.isChecked() and self.channel_2_checkBox.isChecked():
            channel = 12
        elif self.channel_1_checkBox.isChecked():
            channel = 1
        else:
            channel = 2
            
        return channel
 
 
#%% Measurement        
    def StartMeasurement(self):
        # enable stop_measurement_button        
        self.stop_measurement_button.setEnabled(True)
        
        # disable all actions        
        self.data_saved_lineEdit.clear()        
        self.data_saved_lineEdit.setEnabled(False)            
        self.export_data_button.setEnabled(False)
        self.idn_button.setEnabled(False)
        self.instruments_comboBox.setEnabled(False)
        self.integration_time_comboBox.setEnabled(False)
        self.start_measurement_button.setEnabled(False)
        self.scan_instruments_button.setEnabled(False)
        self.channel_1_checkBox.setEnabled(False)
        self.channel_2_checkBox.setEnabled(False)
        self.nr_of_measurements_spinBox.setEnabled(False)
        self.idn_textBox.setEnabled(False)
        
        # initialize table attributes
        self.measurement_data_table.setRowCount(0)
        self.timer_counter = 0
        self.timer.setInterval(self.offset)
        
       
        # get measurement parameters 
        self.channel                = self.GetChannel()
        nplc_index                  = self.integration_time_comboBox.currentIndex()
        nplc                        = self.nplc_list[nplc_index] 
        self.sample_count           = self.nr_of_measurements_spinBox.value()     
        self.digits_sample_count    = len(str(self.sample_count))
        self.nr_string              = '{:' + str(self.digits_sample_count) + '}'
        
        # write parameters to instrument
        if not self.channel == 12:
            self.instrument.write('ROUT:TERM FRON%d'       % self.channel)
        self.instrument.write('SENS:VOLT:DC:NPLC %s'   % nplc)    
        
        # calculate timer offset
        if self.integration_time >= 200: self.offset = int(self.integration_time*2) # NEEDS CHANGE  
         
        # set timeout        
        self.instrument.timeout = int(self.integration_time  + self.offset*0.9)

        # create table
        self.measurement_data_table.setColumnCount(4)
        self.measurement_data_table.insertRow(0)
        self.measurement_data_table.verticalHeader().setVisible(False)
        self.measurement_data_table.setItem(0, 0, QtGui.QTableWidgetItem('Nr.'))
        self.measurement_data_table.setItem(0, 1, QtGui.QTableWidgetItem('Date'))
        self.measurement_data_table.setItem(0, 2, QtGui.QTableWidgetItem('Data on Ch 1 [V]'))
        self.measurement_data_table.setItem(0, 3, QtGui.QTableWidgetItem('Data on Ch 2 [V]'))
#        QtGui.QTableWidget.verticalHeader().setVisible(False)
        
        # Start Measurement
        self.timer.start()
        
        
#        for i in range(sample_count):
#             # START MEASUREMENT
#     
#            measurement_data    = self.instrument.query('READ?')
##            self.measurement_data_table.setItem(i + 1, 0, QtGui.QTableWidgetItem(str(i + 1)))
#            
##            self.filename_lineEdit.setText(measurement_data)
##            print(datetime.datetime.now(),measurement_data)            
#            row_count = self.measurement_data_table.rowCount()
#            self.measurement_data_table.insertRow(row_count)
#            self.measurement_data_table.setItem(row_count, 0, QtGui.QTableWidgetItem(str(datetime.datetime.now())))
#            self.measurement_data_table.setItem(row_count, 1, QtGui.QTableWidgetItem(measurement_data))
#                   
##            self.measurement_data_table.show()

#######################
#        # Set instrumets values to default
#        self.instrument.write('ROUT:TERM FRON1')
#        self.instrument.write('SENS:VOLT:DC:NPLC MIN')    
##        self.instrument.write('SAMP:COUN MIN')
#        self.instrument.timeout = 2000

#        self.measurement_data_table.setItem(0, 1, QtGui.QTableWidgetItem('Date'))
#        self.measurement_data_table.setItem(0, 2, QtGui.QTableWidgetItem('Data [V]'))
#        self.measurement_data_table.setItem(0, 0, QtGui.QTableWidgetItem('Channel 2'))
        
        

       
        
        

#        

#            #QtGui.QTextEdit.se

    
    def TimerMeasurement(self):
        
        
#        # get measurement parameters 
#        channel             = self.channel_spinBox.value()
#        nplc_index          = self.integration_time_comboBox.currentIndex()
#        nplc                = self.nplc_list[nplc_index] 
#        self.sample_count   = self.nr_of_measurements_spinBox.value()     
#        
#        # write parameters to instrument
#        self.instrument.write('ROUT:TERM FRON%d'       % channel)
#        self.instrument.write('SENS:VOLT:DC:NPLC %s'   % nplc)            
#        
#        
        
        # Set timer interval: Must be bigger than device timeout
        self.timer.setInterval(self.integration_time + self.offset)
        
        
        if self.channel == 12:
            # Set timer interval: Must be bigger than device timeout
            self.timer.setInterval(2*(self.integration_time + self.offset))
            
            measurement_data = ['','']            
            
            current_channel = 1
            self.instrument.write('ROUT:TERM FRON%d' % current_channel)
            measurement_data[0]    = self.instrument.query('READ?')[:-1] 
            
            current_channel = 2
            self.instrument.write('ROUT:TERM FRON%d' % current_channel)
            measurement_data[1]    = self.instrument.query('READ?')[:-1]
            
            self.WriteToTableWidget(measurement_data)
            
            
        else:
            # Set timer interval: Must be bigger than device timeout
            self.timer.setInterval(self.integration_time + self.offset)
            # Query 'read', device measures
            measurement_data    = self.instrument.query('READ?')[:-1]
            self.WriteToTableWidget(measurement_data)

        # rescale column width
        self.measurement_data_table.resizeColumnsToContents()        
        

              

        
        # enable auto scroll
#        self.measurement_data_table.autoScrollMargin() #DOES NOT WORK
        
        # increase counter
        self.timer_counter += 1        
        
        # stop measurement if enough data points
        if self.sample_count == self.timer_counter:
            
            # enable all actions except stop_measurement_button            
            self.stop_measurement_button.setEnabled(False)
            self.export_data_button.setEnabled(True)
            self.idn_button.setEnabled(True)
            self.instruments_comboBox.setEnabled(True)
            self.integration_time_comboBox.setEnabled(True)
            self.start_measurement_button.setEnabled(True)
            self.scan_instruments_button.setEnabled(True)
            self.channel_1_checkBox.setEnabled(True)
            self.channel_2_checkBox.setEnabled(True)
            self.nr_of_measurements_spinBox.setEnabled(True)
            self.idn_textBox.setEnabled(True)
            
            # stop measurement            
            self.timer.stop()
#        self.timer.stop()
            
#    def WaitOnEvent(self):
#        self.lib.wait_on_event()
   
   
    def WriteToTableWidget(self, measurement_data):
        
        # write to table
        row_count = self.measurement_data_table.rowCount()
        self.measurement_data_table.insertRow(row_count)
        self.measurement_data_table.setItem(row_count, 0, QtGui.QTableWidgetItem(self.nr_string.format(str(self.timer_counter + 1))))
        self.measurement_data_table.setItem(row_count, 1, QtGui.QTableWidgetItem(str(datetime.datetime.now())[:-7]))
        
        if self.channel == 1:
            self.measurement_data_table.setItem(row_count, 2, QtGui.QTableWidgetItem(measurement_data))
            self.measurement_data_table.setItem(row_count, 3, QtGui.QTableWidgetItem('-'))
           
        elif self.channel == 2:
            self.measurement_data_table.setItem(row_count, 2, QtGui.QTableWidgetItem('-'))
            self.measurement_data_table.setItem(row_count, 3, QtGui.QTableWidgetItem(measurement_data))
        else:
            self.measurement_data_table.setItem(row_count, 2, QtGui.QTableWidgetItem(measurement_data[0]))
            self.measurement_data_table.setItem(row_count, 3, QtGui.QTableWidgetItem(measurement_data[1]))
            
    def StopMeasurement(self):
        # enable all actions except stop_measurement_button            
        self.stop_measurement_button.setEnabled(False)
        self.export_data_button.setEnabled(True)
        self.idn_button.setEnabled(True)
        self.instruments_comboBox.setEnabled(True)
        self.integration_time_comboBox.setEnabled(True)
        self.start_measurement_button.setEnabled(True)
        self.scan_instruments_button.setEnabled(True)
        self.channel_1_checkBox.setEnabled(True)
        self.channel_2_checkBox.setEnabled(True)
        self.nr_of_measurements_spinBox.setEnabled(True)        
        self.idn_textBox.setEnabled(True)
        
        # stop measurement
        self.timer.stop()

#%% CLOSE        
    def closeEvent(self, event):
      
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            # Set instrumets values to default            
            self.instrument.write("*RST")
            event.accept()
        else:
            event.ignore()   
            
            
#%% Export
    def ExportToFile(self):

        self.filename   = self.filename_lineEdit.text()
        textfile        = ExportToTextfile(self.filename, self.idn, self.measurement_data_table)
        success         = textfile.WriteToFile()
        self.data_saved_lineEdit.setEnabled(True)
        self.data_saved_lineEdit.setReadOnly(False)        
        self.data_saved_lineEdit.setText(success)
        self.data_saved_lineEdit.setReadOnly(True)

#%% main
if __name__ == "__main__":
    
    app = QtGui.QApplication.instance()
    if app is None:
        app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.Main()
    window.show()
sys.exit(app.exec_())
