import sys
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import wntr
import inp2cpa


class inp2cpaApp(QtWidgets.QMainWindow):
    def __init__(self, ui):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(ui, self)
        
        self.setWindowTitle('INP2CPA')
        # click  buttons
        self.importINP.clicked.connect(self.importINPfunc)
        self.reassigncybernodes.clicked.connect(self.reassignfunc)
        self.previewFileBtn.clicked.connect(self.previewCPAfile)
        self.save_cpa_btn.clicked.connect(self.saveCPAfile)
        self.availablePLCnames=['2','3','4','5','6','7','8','9','10','11','12','13','14','15','16']
        self.TextToExport=None
        # self.findheadersButton.clicked.connect(self.getHeadersfunc)
        # self.getPart.clicked.connect(self.getPartfunc)
        # self.showDFbutton.clicked.connect(self.showDFfunc)
        # self.findCommentsButton.clicked.connect(self.getCommentsfunc)        
        # self.lastAcquiredPart=pd.DataFrame()
        # self.copyToClipboard.clicked.connect(self.copyfunc)
        # self.renameElements.clicked.connect(self.renameElemenetsfunc)
        # self.parse_rpt.clicked.connect(self.parseRPTfunc)
        # # Initialize whattoparsecombobox
        # self.parseElementComboBox.addItem('Link')
        # self.parseElementComboBox.addItem('Node')
        # self.showDFresultsButton.clicked.connect(self.showRPTdffunc)
        # self.visualizeButton.clicked.connect(self.vizualizeRPTdffunc)
        
        # self.parseAttributeComboBox.addItem('Pressure')
        # self.parseAttributeComboBox.addItem('Pressure')
        
        
    def importINPfunc(self):
        self.in_inpfile= str(QtWidgets.QFileDialog.getOpenFileName(None, "Open .inp water network file", '.', "(*.inp)")[0])
        if self.in_inpfile: 
            self.inp_path.setText('Imported '+str(self.in_inpfile))
            self.cyberTopo=inp2cpa.cyberControlRead(self.in_inpfile)
            self.cpa_dict=inp2cpa.create_topology_cpa_dict(self.cyberTopo)
        else:
            self.inp_path.setText('Nothing imported !')
    
    def previewCPAfile(self):
        formated_string=self.parse_dict() ### where we start the cpa preview
        previewDlg=PreviewDialog(formated_string)
        if previewDlg.exec_():
            self.TextToExport=formated_string
        
            
    def reassignfunc(self):
        newPLCDlg=newPLCDialog(self.cpa_dict)
        if newPLCDlg.exec_():
            pass
        
        
    def parse_dict(self):
        formatted_string='[CYBERNODES]\n'     #### writing cpa file here ### need to find where its storing its info. is it in here or wntr. is it already storeing the available data to write cyberlinks ect or will we need to parse for that
        for PLCkey in self.cpa_dict.keys():
            formatted_string=formatted_string+ str(PLCkey)+'\t'
            sensorlist=self.cpa_dict[PLCkey][0]
            removeChar='[]\''
            senstr=','.join(map(str,sensorlist))
            for character in removeChar:
                senstr = senstr.replace(character, '')
            formatted_string=formatted_string+ senstr+'\t'
            actlist=self.cpa_dict[PLCkey][1]
            actstr=','.join(map(str,actlist))
            for character in removeChar:
                actstr = actstr.replace(character, '')
            formatted_string=formatted_string+ actstr+'\n'
        formatted_string=formatted_string+'[CYBERATTACKS]'+'\n'+'[CYBEROPTIONS]'+'\n' + 'verbosity'+'\t'+'1'+'\n'
        formatted_string=formatted_string+'what_to_store' + '\t'+'everything'+'\n'
        formatted_string=formatted_string+'pda_options' + '\t'+'0.5'+'\t'+'0'+'\t'+'20'+'\t'+'Wagner'
        return formatted_string
    
    def saveCPAfile(self):
        name = str(QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '.', "(*.cpa)")[0])
        # print(name)
        file = open(name,'w')
        text = self.TextToExport
        file.write(text)
        file.close()

class PreviewDialog(QtWidgets.QDialog):
    def __init__(self, newText):
        super(PreviewDialog, self).__init__()
        ### 1st field
        self.TextEdit = QtWidgets.QPlainTextEdit()
        self.TextEdit.appendPlainText(newText)
        self.TextEdit.setMinimumWidth(700)
        ### buttons ok/cancel
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        ### layout of the dalog
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('CPA file preview:', self.TextEdit)
        layout.addWidget(self.button_box)
        ### dialog show
        self.setLayout(layout)
        self.setWindowTitle(".cpa preview")
        self.setMinimumWidth(800)        
        
class newPLCDialog(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        super(newPLCDialog, self).__init__()
        self.cpa_dict=cpa_dict
        ### PLC field
        self.newPLCtxt = QtWidgets.QLineEdit()
        self.newPLCtxt.setMinimumWidth(700)
        ### Sensor field
        self.newSensortxt = QtWidgets.QLineEdit()
        self.newSensortxt.setMinimumWidth(700)
        ### Actuator field
        self.newActuatortxt = QtWidgets.QLineEdit()
        self.newActuatortxt.setMinimumWidth(700)
        ### button CHECK
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check changes')
        self.button_check.clicked.connect(self.check_changes_func)
        ### buttons ok/cancel
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        ## layout of the dalog
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Add PLC names seperated by \',\'', self.newPLCtxt)
        layout.addRow('Add sensor lists \'[...]\' seperated by \',\'', self.newSensortxt)
        layout.addRow('Add actuator lists \'[...]\' seperated by \',\'', self.newActuatortxt)
        layout.addRow('Check changes',self.button_check)
        layout.addWidget(self.button_box)
        ### dialog show
        self.setLayout(layout)
        self.setWindowTitle("Re-assign Cyber Nodes")
        self.setMinimumWidth(800)   
        
    # def check_changes_func(self):
    #     list_of_new_plcs, warningPLC, errorPLC, overwritingPLC1 = self.parsePLCtext()
    #     print(list_of_new_plcs, warningPLC, errorPLC, overwritingPLC1)
    #     list_of_new_sensors, warningSensor, errorSensor = self.parseSensortext()
    #     print(list_of_new_sensors, errorPLC)
        
    # def parsePLCtext(self):
    #     overwritingPLC1=False
    #     warning=[]
    #     error=[]
    #     list_of_new_plcs=[]
    #     text=self.newPLCtxt.text()
    #     text=text.replace(' ','')
    #     text=text.split(',')
    #     for plc in text:
    #         if plc in self.cpa_dict.keys():
    #             warning.append(str(plc)+' is already in the .cpa file, line will be overwritten')
    #             if plc == 'PLC1':
    #                 overwritingPLC1=True # This triggers a special condition
    #                 list_of_new_plcs.append(plc)
    #         if plc in list_of_new_plcs:
    #             error.append(str(plc)+' is given multiple times, please revise')
    #         list_of_new_plcs.append(plc)
    #     return list_of_new_plcs, warning, error, overwritingPLC1
    
    # def parseSensortext(self):
    #     warning=[]
    #     error=[]
    #     list_of_new_sensors=[]
    #     text=self.newSensortxt.text()
    #     text=text.replace(' ','')
    #     start = '['
    #     end = ']'
    #     s=text.split(start)
    #     list_of_new_sensors=[]
    #     for i in s:
    #         if i:
    #             i=i.split(end)
    #             list_of_new_sensors.append(i[0])
    #     # make list of the contents of the list_of_new_sensors
    #     list_of_new_sensors=[x.split(',') for x in list_of_new_sensors]
        
    #     for sensors_l in list_of_new_sensors:
    #         if plc in self.cpa_dict.keys():
    #             warning.append(str(plc)+' is already in the .cpa file, line will be overwritten')
    #             if plc == 'PLC1':
    #                 overwritingPLC1=True # This triggers a special condition
    #                 list_of_new_plcs.append(plc)
    #         if plc in list_of_new_plcs:
    #             error.append(str(plc)+' is given multiple times, please revise')
    #         list_of_new_plcs.append(plc)
    #     return list_of_new_plcs, warning, error, overwritingPLC1

    # def parseActuatortext(self):
    #     warning=[]
    #     error=[]
    #     list_of_new_actuators=[]
    #     text=self.newActuatortxt.text()
    #     text=text.replace(' ','')
    #     start = '['
    #     end = ']'
    #     s=text.split(start)
    #     list_of_new_actuators=[]
    #     for i in s:
    #         if i:
    #             i=i.split(end)
    #             list_of_new_actuators.append(i[0])
    #     # make list of the contents of the list_of_new_sensors
    #     list_of_new_actuators=[x.split(',') for x in list_of_new_actuators]

    def check_changes_func(self):
        list_of_new_plcs = self.parsePLCtext()
        print(list_of_new_plcs)
        list_of_new_sensors = self.parseSensortext()
        print(list_of_new_sensors)
        list_of_new_actuators = self.parseActuatortext()
        print(list_of_new_actuators)
        
    def parsePLCtext(self):
        #overwritingPLC1=False
        warning=[]
        error=[]
        list_of_new_plcs=[]
        text=self.newPLCtxt.text()
        text=text.replace(' ','')
        text=text.split(',')
        for plc in text:
            #if plc in self.cpa_dict.keys():
                #warning.append(str(plc)+' is already in the .cpa file, line will be overwritten')
               # if plc == 'PLC1':
                    #overwritingPLC1=True # This triggers a special condition
                    #list_of_new_plcs.append(plc)
            #if plc in list_of_new_plcs:
                #error.append(str(plc)+' is given multiple times, please revise')
            list_of_new_plcs.append(plc) ### adding to our list
        return list_of_new_plcs
    
    def parseSensortext(self):
        warning=[]
        error=[]
        list_of_new_sensors=[]
        text=self.newSensortxt.text()
        text=text.replace(' ','')
        start = '['
        end = ']'
        s=text.split(start)
        list_of_new_sensors=[]
        for i in s:
            if i:
                i=i.split(end)
                list_of_new_sensors.append(i[0])
        # make list of the contents of the list_of_new_sensors
        list_of_new_sensors=[x.split(',') for x in list_of_new_sensors]
        
        for sensor in list_of_new_sensors:
            list_of_new_sensors.append(sensor)
        return list_of_new_sensors

    def parseActuatortext(self):
        warning=[]
        error=[]
        list_of_new_actuators=[]
        text=self.newActuatortxt.text()
        text=text.replace(' ','')
        start = '['
        end = ']'
        s=text.split(start)
        list_of_new_actuators=[]
        for i in s:
            if i:
                i=i.split(end)
                list_of_new_actuators.append(i[0])
        # make list of the contents of the list_of_new_Acuators
        list_of_new_actuators=[x.split(',') for x in list_of_new_actuators]
        for actuator in list_of_new_actuators:
            list_of_new_actuators.append(actuator)
        return list_of_new_actuators

