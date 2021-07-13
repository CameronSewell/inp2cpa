from logging import PlaceHolder
from os import remove
import sys
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import re

import wntr
import inp2cpa

class storage:
    def store(self):
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
        """Initializes main INP2CPA window, including creating buttons linked to their respective functions. """
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
        self.setFixedWidth(580)
        self.setFixedHeight(100)
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
            self.inp_path.setText('Nothing Imported!')
    
    def previewCPAfile(self):
        formated_string=self.parse_dict() 
        previewDlg=PreviewDialog(formated_string)
        if previewDlg.exec_():
            self.TextToExport=formated_string
        
            
    def reassignfunc(self):
        newPLCDlg=newPLCDialog(self.cpa_dict)
        if newPLCDlg.exec_():
            pass

    def addLinks(self):
        newLinkDlg = cyberLinkDialog(self.cpa_dict)
        if newLinkDlg.exec_():
            pass
    
    def addAttack(self):
        attackDlg = cyberAttackDialog(self.cpa_dict)
        if attackDlg.exec_():
            pass

    # def modOptions(self):
    # pass

    def parse_dict(self):
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
                
        
class newPLCDialog(QtWidgets.QDialog):
    warningNo = 0
    warning=['', 'Warning: Format each sensor with only one underscore', 'Warning: Each sensor must begin with \'P_\', \'F_\', \'S_\', or \'SE_\'.']
    def __init__(self, cpa_dict):
        super(newPLCDialog, self).__init__()
        self.cpa_dict=cpa_dict

        ### PLC field
        self.newPLCtxt = QtWidgets.QLineEdit()
        ### Sensor field
        self.newSensortxt = QtWidgets.QLineEdit()
        ### Actuator field
        self.newActuatortxt = QtWidgets.QLineEdit()

        ### Warning label
        self.warningtxt = QtWidgets.QLabel(self.warning[self.warningNo])
        self.warningtxt.setStyleSheet("""
        QWidget {
            color: red;
            }
        """)
        
        ### Check Changes and Update Warning Label
        def updateChanges (event):
            self.check_changes_func()
            print ('update changes ', self.warningNo)
            self.warningtxt.setText(self.warning[self.warningNo])

        ### button CHECK
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check Changes')
        self.button_check.clicked.connect(updateChanges)
        ### buttons ok/cancel
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.addButton(self.button_check, QDialogButtonBox.ActionRole)
        
        ### QApplication::setStyle()?? enforce style across different operating systems

        ## layout of the dialog
        outerLayout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QVBoxLayout()
        buttonLayout = QtWidgets.QHBoxLayout()
        #layout.setSpacing(0)
        myFont = QtGui.QFont()
        myFont.setBold(True)
        #layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        plcnames = QLabel('PLC Names')
        plcnames.setFont(myFont)
        layout.addWidget(plcnames)
        layout.addWidget(QLabel('Separate each name by \',\''))
        layout.addWidget(self.newPLCtxt)
        sensors = QLabel('Sensors')
        sensors.setFont(myFont)
        layout.addWidget(sensors)
        layout.addWidget(QLabel('Separate sensors within a group by \'  \'' ' separate sensor lists by \',\''))
        layout.addWidget(self.newSensortxt)
        actuators = QLabel('Actuators')
        actuators.setFont(myFont)
        layout.addWidget(actuators)
        layout.addWidget(QLabel('Separate actuators within a group by \'  \'' ' separate actuator lists by \',\''))
        layout.addWidget(self.newActuatortxt)
        # layout.addWid('Add PLC names separated by \',\'', self.newPLCtxt)
        # layout.addRow('Add sensor groups separated by a \'  \'' ' sensor lists separated by \',\'', self.newSensortxt)
        # layout.addRow('Add actuator groups separated by a \'  \'' ' actuator lists separated by \',\'', self.newActuatortxt)
        #layout.addRow(self.button_check)

        layout.addWidget(self.warningtxt)
        buttonLayout.addWidget(self.button_check) 
        buttonLayout.addWidget(self.button_box)
        #layout.addWidget(self.button_check)
        outerLayout.addLayout(layout)
        outerLayout.addLayout(buttonLayout)
        self.setLayout(outerLayout)

        ### dialog show
        #self.setLayout(layout)
        self.setWindowTitle("Re-Assign Cyber Nodes")
        #self.setMinimumWidth(800) 
        self.setFixedWidth(600)
        self.setFixedHeight(350)  

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

        text=text.split(',')
        for plc in text:
            list_of_new_plcs.append(plc)
            # if (re.search('_.*_', plc)):
            #     self.warningNo=1
            #     list_of_new_plcs.append(plc)
            # else: 
            #     self.warningNo=0
            #     list_of_new_plcs.append(plc)
        #list_of_new_plcs.append(plc)
        return list_of_new_plcs
    
    def parseSensortext(self):
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
                    print ('__ ',tempWarning)
                if not (re.search('^S_', sensor) or re.search('^F_', sensor) or re.search('^P_', sensor) or re.search ('^SE_', sensor)):                    
                    tempWarning=2
                    print ('incorrect prefix ', tempWarning)
            list_of_new_sensors.append(sensorGroup)
        print ('final ', tempWarning)
        self.warningNo = tempWarning
        print('warningNo ', self.warningNo)
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

    def parseActuatortext(self):
        list_of_new_actuators = []
        text = self.newActuatortxt.text()
        text = text.split(',')
        for actuator in text:
            list_of_new_actuators.append(actuator)
        return list_of_new_actuators

class cyberLinkDialog(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        super(cyberLinkDialog, self).__init__()
        ###Source field
        self.newSourcetxt = QtWidgets.QLineEdit()
        ###Destination field
        self.newDestinationtxt = QtWidgets.QLineEdit()
        ###Sensor field
        self.newSensortxt = QtWidgets.QLineEdit()
        ###Check changes
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check Changes')
        self.button_check.clicked.connect(self.link_check)
        ###Button ok/cancel
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        ## create layouts 
        outerLayout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QVBoxLayout()
        buttonLayout = QtWidgets.QHBoxLayout()

        myFont = QtGui.QFont()
        myFont.setBold(True)

        ### Label and entry layout
        sourceNames = QLabel('Source Names')
        sourceNames.setFont(myFont)
        layout.addWidget(sourceNames)
        layout.addWidget(QLabel('Separate each source name by \',\''))
        layout.addWidget(self.newSourcetxt)
        destinationNames = QLabel('Destination Names')
        destinationNames.setFont(myFont)
        layout.addWidget(destinationNames)
        layout.addWidget(QLabel('Separate destination names by \',\''))
        layout.addWidget(self.newDestinationtxt)
        actuators = QLabel('Sensors')
        actuators.setFont(myFont)
        layout.addWidget(actuators)
        layout.addWidget(QLabel('Separate sensor names by \',\''))
        layout.addWidget(self.newSensortxt)
        layout.addWidget(QLabel(""))

        ### Check changes and ok/cancel buttons
        buttonLayout.addWidget(self.button_check) 
        buttonLayout.addWidget(self.button_box)

        ### Set layouts
        outerLayout.addLayout(layout)
        outerLayout.addLayout(buttonLayout)
        self.setLayout(outerLayout)

        ### Set window properties
        self.setWindowTitle("Create Cyber Links")
        self.setFixedWidth(600)
        self.setFixedHeight(350) 

    def parseNewSource(self):
        list_of_sources=[]
        text=self.newSourcetxt.text()
        text=text.replace(' ','')
        text=text.split(',')
        for source in text:
            list_of_sources.append(source)
        return list_of_sources
    def parseNewDestination(self):
        list_of_destinations=[]
        text=self.newDestinationtxt.text()
        text=text.replace(' ','')
        text=text.split(',')
        for destination in text:
            list_of_destinations.append(destination)
        return list_of_destinations
    def parseNewSensor(self):
        list_of_sensors=[]
        text=self.newSensortxt.text()
        text=text.split(',')
        for sensor in text:
            list_of_sensors.append(sensor)
        return list_of_sensors

    def link_check(self):
        storage.list_of_new_sources = self.parseNewSource()
        storage.list_of_new_destinations = self.parseNewDestination()
        storage.list_of_new_link_sensors = self.parseNewSensor()
        print(storage.list_of_new_sources)
        print(storage.list_of_new_destinations)
        print(storage.list_of_new_link_sensors)
        inp2cpaApp.hasCyberLinks = True

class cyberAttackDialog(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        super(cyberAttackDialog, self).__init__()
        ### Attack Type Button
        self.button_comm = QtWidgets.QPushButton()
        self.button_comm.setText('Communication')
        self.button_comm.clicked.connect(cyberAttackDialog.comm_window)
        self.button_act = QtWidgets.QPushButton()
        self.button_act.setText('Actuator')
        self.button_act.clicked.connect(cyberAttackDialog.act_window)
        self.button_sen = QtWidgets.QPushButton()
        self.button_sen.setText('Sensor')
        self.button_sen.clicked.connect(cyberAttackDialog.sen_window)
        self.button_con = QtWidgets.QPushButton()
        self.button_con.setText('Control')
        self.button_con.clicked.connect(cyberAttackDialog.con_window)
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

    def comm_window(self): ################################## just make it its own class
        #super(cyberAttackDialog, self).__init__()
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
        ####layout
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Enter the target link (i.e. P_tank1-PLC1)', self.targetTxt)
        layout.addRow('Enter the initial condition', self.initCTxt)
        layout.addRow('Enter the ending condition', self.endCTxt)
        layout.addRow('Enter the attack arguments', self.argTxt)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)

    def sen_window(self):
        pass

    def act_window(self):
        pass

    def con_window(self):
        pass