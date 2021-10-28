from logging import PlaceHolder
from os import link, remove
import sys
from xml.etree.ElementTree import parse
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import re

import wntr
import inp2cpa

cpa_dict = None
pathName = ""

class storage:
    def store(self):
        """Creates lists to store the CPA file data."""
        self.list_of_new_plcs = []
        self.list_of_new_sensors = []
        self.list_of_new_actuators = []
        self.list_of_new_sources = []
        self.list_of_new_destinations = []
        self.list_of_new_link_sensors = []

class inp2cpaApp(QtWidgets.QMainWindow):
    isAltered = False
    hasCyberLinks = False
    hasAttacks = False

    def __init__(self, ui):
        """Opens the Import .inp window to allow the user to select an inp. file."""
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(ui, self)
        
        self.setWindowTitle('INP2CPA')
        # click  buttons
        self.importINP.clicked.connect(self.importINPfunc)
        self.reassigncybernodes.clicked.connect(self.reassignfunc)
        self.addCyberAttacks.clicked.connect(self.addAttack)
        #self.modifyCyberOptions.clicked.connect(self.modOptions)
        self.makeCyberLinks.clicked.connect(self.addLinks)
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
            """Connected to the 'import .inp' button. 
            Imports an .inp file. If nothing is selected, displays 'Nothing Imported!'"""
            in_inpfile= str(QtWidgets.QFileDialog.getOpenFileName(None, "Open .inp water network file", '.', "(*.inp)")[0])
            if (len(in_inpfile)>0): 
                pathname.setStyleSheet('color: black')
                pathname.setText(str(in_inpfile))
                global pathName
                pathName = in_inpfile
                cyberTopo=inp2cpa.cyberControlRead(in_inpfile)
                global cpa_dict
                cpa_dict = inp2cpa.create_topology_cpa_dict(cyberTopo)
            else:
                pathname.setText('Nothing Imported!')
    
    def previewCPAfile(self):
        formated_string=self.parse_dict() 
        previewDlg=PreviewDialog(formated_string)
        if previewDlg.exec_():
            self.TextToExport=formated_string
        
            
    def reassignfunc(self):
            """Connected to the 'Re-Assign CyberNodes' button. 
            This function calles the newPLCDialog function (creates the Re-Assign CyberNodes window)."""
            newPLCDlg=newPLCDialog(cpa_dict)
            if newPLCDlg.exec_():
                pass

    def addLinks(self):
            """Connected to the 'Create CyberLinks' button. 
            This function calles the CyberLinkDialog function (creates the Create CyberLinks window)."""
            newLinkDlg = cyberLinkDialog(cpa_dict)
            if newLinkDlg.exec_():
                pass
    
    def addAttack(self):
            """Connected to the 'Create CyberAttacks' button. 
            This function calles the cyberAttackDialog function (creates the Choose an Attack Type window)."""
            attackDlg = cyberAttackDialog(cpa_dict)
            if attackDlg.exec_():
                pass

    # def modOptions(self):
    # pass

    def parse_dict(self):
        """Called by previewCPAfile. 
            Parses imported .inp file, and creates the base/starting .cpa file from the import, stored in the storage class."""
        if inp2cpaApp.isAltered:
            formatted_string = '[CYBERNODES]\n;Name,\tSensors,\tActuators\n'
            for x in range(len(storage.list_of_new_plcs)):
                range(len(storage.list_of_new_sensors))
                range(len(storage.list_of_new_actuators))
                formatted_string = formatted_string + str(storage.list_of_new_plcs[x]) + ',\t' + str(storage.list_of_new_sensors[x]) + ',\t' + str(storage.list_of_new_actuators[x]) + '\n'
            if inp2cpaApp.hasCyberLinks:
                formatted_string  = formatted_string + '[CYBERLINKS]\n;Source,\tDestination,\tSensors\n' 
                for x in range(len(storage.list_of_new_sources)):
                    range(len(storage.list_of_new_destinations))
                    range(len(storage.list_of_new_link_sensors))
                    formatted_string = formatted_string + str(storage.list_of_new_sources[x]) + ',\t' + str(storage.list_of_new_destinations[x]) + ',\t' + str(storage.list_of_new_link_sensors[x]) + '\n'

            else:
                formatted_string  = formatted_string + '[CYBERLINKS]\n;Source,\tDestination,\tSensors\n'   
            formatted_string = formatted_string + '[CYBERATTACKS]\n;Type,\tTarget,\tInit_cond,\tEnd_cond,\tArguments\n'
            formatted_string = formatted_string + '[CYBEROPTIONS]\n' + 'verbosity'+ '\t' +'1' +'\n'
            formatted_string = formatted_string + ';what_to_store' + '\t'+'everything'+'\n'
            formatted_string = formatted_string + ';pda_options' + '\t' + '0.5' + '\t' + '0' + '\t' + '20' + '\t' + 'Wagner'
            return formatted_string
        else:
            formatted_string='[CYBERNODES]\n'   
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
            formatted_string = formatted_string+ actstr+'\n'
            formatted_string = formatted_string+'[CYBERATTACKS]'+'\n'+'[CYBEROPTIONS]'+'\n' + 'verbosity'+'\t'+'1'+'\n'
            formatted_string = formatted_string+'what_to_store' + '\t'+'everything'+'\n'
            formatted_string = formatted_string+'pda_options' + '\t'+'0.5'+'\t'+'0'+'\t'+'20'+'\t'+'Wagner'
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
    warningNo = 0
    warning=['', 'Warning: Format each cybernode with only one underscore', 'Warning: No PLCs entered']
    def __init__(self, cpa_dict):
        super(newPLCDialog, self).__init__()
        self.cpa_dict=cpa_dict
        self.setFixedWidth(1200)
        self.setFixedHeight(200)
        ### PLC field
        self.newPLCtxt = QtWidgets.QLineEdit()
        self.newPLCtxt.setMinimumWidth(700)
        ### Sensor field
        self.newSensortxt = QtWidgets.QLineEdit()
        self.newSensortxt.setMinimumWidth(700)
        ### Actuator field
        self.newActuatortxt = QtWidgets.QLineEdit()
        self.newActuatortxt.setMinimumWidth(700)
        ### Warning label
        self.warningtxt = QtWidgets.QLabel(self.warning[self.warningNo])
        ### Check Changes and Update Warning Label
        def updateChanges (event):
            self.check_changes_func()
            self.warningtxt.setText(self.warning[self.warningNo])
        ### button CHECK
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check Changes')
        self.button_check.clicked.connect(updateChanges)
        ### buttons ok/cancel
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        ## layout of the dialog
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Add PLC names seperated by \',\'', self.newPLCtxt)
        layout.addRow('Add sensor groups seperated by a \'  \'' ' sensor lists seperated by \',\'', self.newSensortxt)
        layout.addRow('Add actuator groups seperated by a \'  \'' ' actuator lists seperated by \',\'', self.newActuatortxt)
        layout.addRow('Check changes',self.button_check)
        layout.addWidget(self.button_box)
        layout.addWidget(self.warningtxt)
        ### dialog show
        self.setLayout(layout)
        self.setWindowTitle("Re-Assign Cyber Nodes")
        self.setMinimumWidth(800)   

    def check_changes_func(self):
        storage.list_of_new_plcs = self.parsePLCtext()
        print(storage.list_of_new_plcs)
        storage.list_of_new_sensors = self.parseSensortext()
        print(storage.list_of_new_sensors)
        storage.list_of_new_actuators = self.parseActuatortext()
        print(storage.list_of_new_actuators)
        inp2cpaApp.isAltered = True
        print(self.warningNo)
        
    def parsePLCtext(self):
        #overwritingPLC1=False
        error=[]
        list_of_new_plcs=[]
        text=self.newPLCtxt.text()
        #text=text.replace(' ','')
        if (len(text)==0):
            self.warningNo=2
        text=text.split(',')
        for plc in text:
            if (re.search('_.*_', plc)):
                self.warningNo=1
            if (len(text)==0):
                self.warningNo=2
            list_of_new_plcs.append(plc)
        return list_of_new_plcs
    
    # def parseSensortext(self):
    #     #warning=[]
    #     #error=[]
    #     list_of_new_sensors=[]
    #     text=text=self.newSensortxt.text()
    #     text=text.replace(' ','')
    #     start = '['
    #     end = ']'
    #     s=text.split(start)
    #     list_of_new_sensors=[]
    #     for i in s:
    #         if i:
    #          i=i.split(end)
    #          list_of_new_sensors.append(i[0])
    #     list_of_new_sensors=[x.split(',') for x in list_of_new_sensors]
    #     return(list_of_new_sensors)
    def parseSensortext(self):
        """Called by the check_changes_func function.
        Splits the user's sensor input by commas, and adds the sensors to a list. 
        A warning is displayed if the input is potentially invalid. Returns the list."""
        list_of_new_sensors = []
        text = self.newSensortxt.text()
        if (len(text)==0):
            self.warningNo=0
            return list_of_new_sensors
        text = text.split(',')
        tempWarning = 0
        for sensorGroup in text:
            indivSensor = sensorGroup.split(' ')
            for sensor in indivSensor:
                if (re.search('_.*_', sensor)):
                    tempWarning=1
                    # print ('__ ',tempWarning)
                if not (re.search('^S_', sensor) or re.search('^F_', sensor) or re.search('^P_', sensor) or re.search ('^SE_', sensor)):                    
                    tempWarning=2
                    # print ('incorrect prefix ', tempWarning)
            list_of_new_sensors.append(sensorGroup)
        self.warningNo = tempWarning
        return list_of_new_sensors

    # def parseActuatortext(self):
    #     #warning=[]
    #     #error=[]
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
    #     list_of_new_actuators=[x.split(',') for x in list_of_new_actuators]
    #     return list_of_new_actuators
    #TODO: Add futher parsing of text in the style of parseSensorText
    def parseActuatortext(self):
        """Called by the check_changes_func function.
        Splits the user's actuator input by commas, adds the acutators to a list, and returns the list."""
        list_of_new_actuators = []
        text = self.newActuatortxt.text()
        text = text.split(',')
        for actuator in text:
            list_of_new_actuators.append(actuator)
        return list_of_new_actuators

##class cyberLinkDialog(QtWidgets.QDialog):
   ## def __init__(self, cpa_dict):
       ## super(cyberLinkDialog, self).__init__()
        ###Source field
       ##self.newSourcetxt = QtWidgets.QLineEdit()
        ##self.newSourcetxt.setMinimumWidth(700)
        ###Destination field
        ##self.newDestinationtxt = QtWidgets.QLineEdit()
        ##self.newDestinationtxt.setMinimumWidth(700)
        ###Sensor field
        ##self.newSensortxt = QtWidgets.QLineEdit()
        ##self.newSensortxt.setMinimumWidth(700)
        ###Check changes
        ##self.button_check = QtWidgets.QPushButton()
        ##self.button_check.setText('Check changes')
        ##self.button_check.clicked.connect(self.link_check)
        ###Button ok/cancel
        ##self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        ##self.button_box.accepted.connect(self.accept)
        ##self.button_box.rejected.connect(self.reject)
        ###Layout
        ##layout = QtWidgets.QFormLayout()
        ##layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        ##layout.addRow('Add Source names seperated by \',\'', self.newSourcetxt)
        ##layout.addRow('Add Destination names seperated by \',\'', self.newDestinationtxt)
        ##layout.addRow('Add Sensor names seperated by \',\'', self.newSensortxt)
        ##layout.addRow('Check changes',self.button_check)
        ##layout.addWidget(self.button_box)
        ###Show Dialog
        ##self.setLayout(layout)
        ##self.setWindowTitle("Create Cyber Links")
        ##self.setMinimumWidth(800)
class cyberAttackDialog(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        """Called by the addAttack function.
        Creates the Choose an Attack Type window with buttons to select a type of attack to create."""
        super(cyberAttackDialog, self).__init__()
        ### Attack Type Button
        self.button_comm = QtWidgets.QPushButton()
        self.button_comm.setText('Communication')
        self.button_comm.clicked.connect(self.call_comm)
        self.button_act = QtWidgets.QPushButton()
        self.button_act.setText('Actuator')
        self.button_act.clicked.connect(self.call_act)
        self.button_sen = QtWidgets.QPushButton()
        self.button_sen.setText('Sensor')
        self.button_sen.clicked.connect(self.call_sen)
        self.button_con = QtWidgets.QPushButton()
        self.button_con.setText('Control')
        self.button_con.clicked.connect(self.call_con)
        ### buttons ok/cancel
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        ###layout
        layout = QtWidgets.QFormLayout()
        layout.addRow(self.button_comm)
        layout.addRow(self.button_con)
        layout.addRow(self.button_sen)
        layout.addRow(self.button_act)
        layout.addWidget(self.button_box)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Choose an attack type")
        self.setMinimumWidth(800)

    def call_sen(self):
        s = sen_window(self)
        if s.exec_():
            pass
    def call_act(self):
        at = act_window(self)
        if at.exec_():
            pass
    def call_con(self):
        co = con_window(self)
        if co.exec_():
            pass
    def call_comm(self):
        cw = comm_window(self)
        if cw.exec_():
            pass

class comm_window(QtWidgets.QDialog): 
    def __init__(self, cpa_dict):
        """Called when the 'Communication' button is pressed in the Choose an Attack Type window.
        Generates a window for creating a communication CyberAttack."""
        super(comm_window, self).__init__()
        ###Target
        self.targetTxt = QtWidgets.QLineEdit()
        self.targetTxt.setMinimumWidth(350)
        ###init_cond
        self.initCTxt = QtWidgets.QLineEdit()
        self.initCTxt.setMinimumWidth(350)
        ###end_cond
        self.endCTxt = QtWidgets.QLineEdit()
        self.endCTxt.setMinimumWidth(350)
        ###arguments
        self.argTxt = QtWidgets.QLineEdit()
        self.argTxt.setMinimumWidth(350)
        ###buttons
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        ###Check changes
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check changes')
        self.button_check.clicked.connect(self.comm_check)
        ####layout
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Enter the target link (i.e. P_tank1-PLC1)', self.targetTxt)
        layout.addRow('Enter the initial condition', self.initCTxt)
        layout.addRow('Enter the ending condition', self.endCTxt)
        layout.addRow('Enter the attack arguments', self.argTxt)
        layout.addRow('Check Changes',self.button_check)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)

    def comm_check(self):
        storage.store.list_of_targets = storage.list_of_targets.extend(parseAttacks.parseTarget(self.targetTxt.text()))
        storage.list_of_icocd = storage.list_of_icocd.extend(parseAttacks.parseICond(self.initCTxt.text()))
        storage.list_of_econd = storage.list_of_econd.extend(parseAttacks.parseECond(self.endCTxt.text()))
        storage.list_of_arg = storage.list_of_arg.extend(parseAttacks.parseArg(self.argTxt.text()))
        print(storage.list_of_targets)
        print(storage.list_of_icocd)
        print(storage.list_of_econd)
        print(storage.list_of_arg)
        inp2cpaApp.hasAttacks = True

class act_window(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        """Called when the 'Actuator' button is pressed in the Choose an Attack Type window.
        Generates a window for creating an actuator CyberAttack."""
        super(act_window, self).__init__()
        ###Target
        self.targetTxt = QtWidgets.QLineEdit()
        self.targetTxt.setMinimumWidth(350)
        ###init_cond
        self.initCTxt = QtWidgets.QLineEdit()
        self.initCTxt.setMinimumWidth(350)
        ###end_cond
        self.endCTxt = QtWidgets.QLineEdit()
        self.endCTxt.setMinimumWidth(350)
        ###arguments
        self.argTxt = QtWidgets.QLineEdit()
        self.argTxt.setMinimumWidth(350)
        ###buttons
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        ###Check changes
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check changes')
        self.button_check.clicked.connect(self.act_check)
        ####layout
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Enter the target actuator', self.targetTxt)
        layout.addRow('Enter the initial condition', self.initCTxt)
        layout.addRow('Enter the ending condition', self.endCTxt)
        layout.addRow('Enter the attack arguments', self.argTxt)
        layout.addRow('Check Changes',self.button_check)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)

    def act_check(self):
        storage.list_of_targets = storage.list_of_targets.extend(parseAttacks.parseTarget(self.targetTxt.text()))
        storage.list_of_icocd = storage.list_of_icocd.extend(parseAttacks.parseICond(self.initCTxt.text()))
        storage.list_of_econd = storage.list_of_econd.extend(parseAttacks.parseECond(self.endCTxt.text()))
        storage.list_of_arg = storage.list_of_arg.extend(parseAttacks.parseArg(self.argTxt.text()))
        print(storage.list_of_targets)
        print(storage.list_of_icocd)
        print(storage.list_of_econd)
        print(storage.list_of_arg)
        inp2cpaApp.hasAttacks = True

class con_window(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        """Called when the 'Control' button is pressed in the Choose an Attack Type window.
        Generates a window for creating a control CyberAttack."""
        super(con_window, self).__init__()
        ###Target
        self.targetTxt = QtWidgets.QLineEdit()
        self.targetTxt.setMinimumWidth(350)
        ###init_cond
        self.initCTxt = QtWidgets.QLineEdit()
        self.initCTxt.setMinimumWidth(350)
        ###end_cond
        self.endCTxt = QtWidgets.QLineEdit()
        self.endCTxt.setMinimumWidth(350)
        ###arguments
        self.argTxt = QtWidgets.QLineEdit()
        self.argTxt.setMinimumWidth(350)
        ###buttons
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        ###Check changes
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check changes')
        self.button_check.clicked.connect(self.con_check)
        ####layout
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Enter the target link or node (i.e. CTRL01l, CTRL01n)', self.targetTxt)
        layout.addRow('Enter the initial condition', self.initCTxt)
        layout.addRow('Enter the ending condition', self.endCTxt)
        layout.addRow('Enter the attack arguments', self.argTxt)
        layout.addRow('Check Changes',self.button_check)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)

    def con_check(self):
        storage.list_of_targets = storage.list_of_targets.extend(parseAttacks.parseTarget(self.targetTxt.text()))
        storage.list_of_icocd = storage.list_of_icocd.extend(parseAttacks.parseICond(self.initCTxt.text()))
        storage.list_of_econd = storage.list_of_econd.extend(parseAttacks.parseECond(self.endCTxt.text()))
        storage.list_of_arg = storage.list_of_arg.extend(parseAttacks.parseArg(self.argTxt.text()))
        print(storage.list_of_targets)
        print(storage.list_of_icocd)
        print(storage.list_of_econd)
        print(storage.list_of_arg)
        inp2cpaApp.hasAttacks = True

class sen_window(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        """Called when the 'Sensor' button is pressed in the Choose an Attack Type window.
        Generates a window for creating a sensor CyberAttack."""
        super(sen_window, self).__init__()
        ###Target
        self.targetTxt = QtWidgets.QLineEdit()
        self.targetTxt.setMinimumWidth(350)
        ###init_cond
        self.initCTxt = QtWidgets.QLineEdit()
        self.initCTxt.setMinimumWidth(350)
        ###end_cond
        self.endCTxt = QtWidgets.QLineEdit()
        self.endCTxt.setMinimumWidth(350)
        ###arguments
        self.argTxt = QtWidgets.QLineEdit()
        self.argTxt.setMinimumWidth(350)
        ###buttons
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        ###Check changes
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check changes')
        self.button_check.clicked.connect(self.sen_check)
        ####layout
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Enter the target sensor', self.targetTxt)
        layout.addRow('Enter the initial condition', self.initCTxt)
        layout.addRow('Enter the ending condition', self.endCTxt)
        layout.addRow('Enter the attack arguments', self.argTxt)
        layout.addRow('Check Changes',self.button_check)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)

    def sen_check(self):
        #storage.list_of_targets = storage.list_of_targets.extend(parseAttacks.parseTarget(self.targetTxt.text()))
        #storage.list_of_icocd = storage.list_of_icocd.extend(parseAttacks.parseICond(self.initCTxt.text()))
        #storage.list_of_econd = storage.list_of_econd.extend(parseAttacks.parseECond(self.endCTxt.text()))
        #storage.list_of_arg = storage.list_of_arg.extend(parseAttacks.parseArg(self.argTxt.text()))
        storage.list_of_targets.extend(parseAttacks.parseTarget(self.targetTxt.text()))
        storage.list_of_icocd.extend(parseAttacks.parseICond(self.initCTxt.text()))
        storage.list_of_econd.extend(parseAttacks.parseECond(self.endCTxt.text()))
        storage.list_of_arg.extend(parseAttacks.parseArg(self.argTxt.text()))
        print(storage.list_of_targets)
        print(storage.list_of_icocd)
        print(storage.list_of_econd)
        print(storage.list_of_arg)
        inp2cpaApp.hasAttacks = True

class parseAttacks:
    def parseTarget(self):
        list_of_targets = []
        text = self
        text = text.split(',')
        for target in text:
            list_of_targets.append(target)
        return list_of_targets

    def parseICond(self):
        list_of_icons = []
        text = self
        text = text.split(',')
        for con in text:
            list_of_icons.append(con)
        return list_of_icons

    def parseECond(self):
        list_of_econs = []
        text = self
        text = text.split(',')
        for con in text:
            list_of_econs.append(con)
        return list_of_econs

    def parseArg(self):
        list_of_args = []
        text = self
        text = text.split(',')
        for arg in text:
            list_of_args.append(arg)
        return list_of_args
