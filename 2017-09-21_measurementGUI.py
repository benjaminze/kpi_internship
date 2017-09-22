import sys
from PyQt4 import QtCore, QtGui, uic
import datetime
import visa


qtCreatorFile = "measureGUI.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        # declare attributes     
        self.rm                      = None
        self.resources               = []
        self.instrument              = None
        self.integration_time        = 0
        self.idn                     = ''
        self.integration_time_list   = ['0.4',  '4','20', '40','200', '400','2000', '4000']
        self.nplc_list               = ['0.02','.2','1',  '2',  '10',  '20', '100',  '200']   
        
        
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
        
        
    def ScanForInstruments(self):
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
         # Get instruments IDN and print in idn_textBox        
        self.idn = self.instrument.query('*IDN?')
        self.idn_textBox.setText(self.idn)


    def GetIntegrationTime(self, index):
        # chosen channel has changed
        self.integration_time = int(self.integration_time_comboBox.currentText())
        
#%% Measurement        
    def StartMeasurement(self):
        # get measurement parameters 
        channel         = self.channel_spinBox.value()
        nplc_index      = self.integration_time_comboBox.currentIndex()
        nplc            = self.nplc_list[nplc_index] 
        sample_count    = self.nr_of_measurements_spinBox.value()     
        
        # write parameters to instrument
        self.instrument.write('ROUT:TERM FRON%d'       % channel)
        self.instrument.write('SENS:VOLT:DC:NPLC %s'   % nplc)    
        self.instrument.write('SAMP:COUN %d'           % sample_count)
        
        # set timeout        
        self.instrument.timeout = int(sample_count * self.integration_time *2 + 3000)
       
        # START MEASUREMENT
        measurement_data    = self.instrument.query('READ?')[:-1] .split(',')
        
        # create string for textbox
        data_to_write    = [0 for i in range(int(sample_count)+2)]
        data_to_write[0] = 'IDN: '+ self.idn
        data_to_write[1] = 'All measurement data in [V]'
        for i in range(len(measurement_data)):
            data_to_write[i+2] = measurement_data[i]        
        
        # print string to textbox
        data_string = ''        
        for item in data_to_write:
            data_string += ('%s\n' %item)
        self.measurement_data_textBox.setText(data_string)
        
        # Set instrumets values to default
        self.instrument.write('ROUT:TERM FRON1')
        self.instrument.write('SENS:VOLT:DC:NPLC MIN')    
        self.instrument.write('SAMP:COUN MIN')
        self.instrument.timeout = 2000
       
#%% main
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MyApp()
    window.Main()
    window.show()
sys.exit(app.exec_())
