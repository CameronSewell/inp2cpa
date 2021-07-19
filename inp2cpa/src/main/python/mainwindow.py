from logging import PlaceHolder
from os import remove
import sys
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import re

import re
import wntr
import inp2cpa

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
        """Connected to the 'import .inp' button. 
        Imports an .inp file. If nothing is selected, displays 'Nothing Imported!'"""
        self.in_inpfile= str(QtWidgets.QFileDialog.getOpenFileName(None, "Open .inp water network file", '.', "(*.inp)")[0])
        if self.in_inpfile: 
            self.inp_path.setText('Imported '+str(self.in_inpfile))
            self.cyberTopo=inp2cpa.cyberControlRead(self.in_inpfile)
            self.cpa_dict=inp2cpa.create_topology_cpa_dict(self.cyberTopo)
        else:
            self.inp_path.setText('Nothing Imported!')
    
    def previewCPAfile(self):
        """Connected to the 'Preview CPA File' button. 
        This function opens the preview CPA window."""
        formated_string=self.parse_dict() 
        previewDlg=PreviewDialog(formated_string)
        if previewDlg.exec_():
            self.TextToExport=formated_string
        
            
    def reassignfunc(self):
        """Connected to the 'Re-Assign Nodes' button. 
        This function calles the newPLCDialog function (creates the Re-Assign CyberNodes window)."""
        newPLCDlg=newPLCDialog(self.cpa_dict)
        if newPLCDlg.exec_():
            pass

    def addLinks(self):
        """Connected to the 'Make CyberLinks' button. 
        This function calles the CyberLinkDialog function (creates the Create CyberLinks window)."""
        newLinkDlg = cyberLinkDialog(self.cpa_dict)
        if newLinkDlg.exec_():
            pass
    
    def addAttack(self):
        """Connected to the 'Add CyberAttacks' button. 
        This function calles the cyberAttackDialog function (creates the Choose an Attack Type window)."""
        attackDlg = cyberAttackDialog(self.cpa_dict)
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
        """Connected to the 'Save .cpa' button. 
        Exports .cpa file to users location of choice."""
        name = str(QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '.', "(*.cpa)")[0])
        # print(name)
        file = open(name,'w')
        text = self.TextToExport
        file.write(text)
        file.close()

class PreviewDialog(QtWidgets.QDialog):
    def __init__(self, newText):
        """Called by the previewCPAfile function. 
        Creates the preview window, showing the user what their .cpa file looks like."""
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
            
    

class CreateHelpWindow(QtWidgets.QDialog):
    def __init__(self, text, title):
        """Called by newPLCDialog.callHelpWindow(). Takes str for the main text, and str for the title of the window.
        Creates a new window with additional information to help the user."""
        super(CreateHelpWindow, self).__init__()
        self.setWindowTitle(title)
        self.resize(400, 500)
        self.setMaximumSize(700, 600)
        self.setMinimumSize(300, 400)
        self.text = text
        layout = QtWidgets.QVBoxLayout()
        textLabel = ScrollLabel(self)
        textLabel.setText(text)
        textLabel.show()
        layout.addWidget(textLabel)
        self.setLayout(layout)

class ScrollLabel(QScrollArea, CreateHelpWindow):
    def __init__(self, *args, **kwargs):
        """Called by CreateHelpWindow. Inherits QScrollArea and CreateHelpWindow.
        Creates a scrollable widget that displays a QLabel."""
        QScrollArea.__init__(self, *args, **kwargs)
        self.setWidgetResizable(True)
        content = QWidget(self)
        self.setWidget(content)
        self.lay = QVBoxLayout(content)
        self.label = QLabel(content)
        self.label.setAlignment(Qt.AlignLeft|Qt.AlignTop)
        self.label.setWordWrap(True)
        self.lay.addWidget(self.label)

    def setText(self, text):
        """Called by CreateHelpWindow. Takes str as a parameter.
        A function that sets the text of the ScrollLabel."""
        self.label.setText(text)



class newPLCDialog(QtWidgets.QDialog):
    warningNo = 0
    warning=['', 'Warning: Format each sensor with only one underscore', 'Warning: Each sensor must begin with \'P_\', \'F_\', \'S_\', or \'SE_\'.']
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
        """Called by the reassignfunc function. 
        Creates the Re-Assign CyberNodes window allowing users to reassign cybernodes through the GUI."""
        super(newPLCDialog, self).__init__()
        self.cpa_dict=cpa_dict
        self.setFixedWidth(1200)
        self.setFixedHeight(200)
        ### PLC field
        self.newPLCtxt = QtWidgets.QLineEdit()
        ### Sensor field
        self.newSensortxt = QtWidgets.QLineEdit()
        ### Actuator field
        self.newActuatortxt = QtWidgets.QLineEdit()
        ### Warning label
        self.warningtxt = QtWidgets.QLabel(self.warning[self.warningNo])
        self.warningtxt.setStyleSheet("""
        QWidget {color: red;}""")
        self.newActuatortxt.setMinimumWidth(700)
        ### Warning label
        self.warningtxt = QtWidgets.QLabel(self.warning[self.warningNo])
        ### Check Changes and Update Warning Label
        def updateChanges (event):
            self.check_changes_func()
            self.warningtxt.setText(self.warning[self.warningNo])

        def callHelpWindow (event):
            """Connected to the '?' button.
            Calls CreateHelpWindow to create the 'Help for Re-Assigning CyberNodes' window."""
            text = ("Re-Assigning CyberNodes\n" 
                    "   This window assists in reassigning PLCs to their respective sensors and acutuators. "
                    "The inputs saved from this screen will replace the current CyberNode data for the new .cpa file.\n\n"
                    "'PLC Names' Field\n"
                    "   Enter PLC names into the first input field, with each name separated by a comma. Do not use a space "
                    "between the names, as the space will become part of the PLC name.\n\n"
                    "Example: \n"
                    "PLC Names: PLC1,PLC2\n\n"
                    "'Sensors' Field\n"
                    "   Enter sensors in the same order as their PLCs were entered. "
                    "The PLCs are linked to the sensors based on the order they are listed in. If multiple sensors are linked to one PLC, "
                    "separate the sensors with a space (' '). To link a sensor to the next PLC in the list, separate the sensors with a "
                    "comma (','). Do not use multiple spaces, or a space and a comma, to separate the sensors, as the space will be aded to the sensor name. "
                    "It is highly suggested that PLC names begin with 'P_', 'S_', 'F_', or 'SE_' to be properly processed and correctly formatted. "
                    "'P_' indicates a sensor montitoring pressure, 'S_' indicates a sensor monitoring status, 'F_' indicates a sensor monitoring flow, "
                    "and 'SE_' indicates a sensor monitoring settings of pumps and valves. Each letter of these prefixes must be capitalized.\n\n"
                    "Example:\n"
                    "PLC Names: PLC1,PLC2\n"
                    "Sensors: P_TANK,S_PUMP1 S_PUMP2\n\n"
                    "   In the above example, PLC1 is connected to the P_TANK sensor, and PLC2 is connected to both sensors S_PUMP1 and S_PUMP2.\n"
                    "   P_TANK is a sensor responsible for monitoring the pressure of the tank, while S_PUMP1 is the sensor monitoring "
                    "the status of PUMP1 and S_PUMP2 is the sensor monitoring the status of PUMP2.\n\n"
                    "'Actuators' Field\n"
                    "   Enter the actuators in the same order as their PLCs were entered. "
                    "The PLS are linked to the actuators based on the order they are listed in. If multiple actuators are linked to one PLC, "
                    "separate the actuators with a space (' '). To link an actuator to the next PLC in the list, separate the actuators with a "
                    "comma (','). Do not use multiple spaces, or a space and a comma, to separate the actuators as the space will be added to the actuator name. \n\n"
                    "Example:\n"
                    "PLC Names: PLC1,PLC2\n"
                    "Sensors: P_TANK,S_PUMP1 S_PUMP2\n"
                    "Actuators:  ,PUMP1 PUMP2\n\n"
                    "   In the above example, PLC1 is not connected to any actuators, and PLC2 is connected to the actuators called PUMP1 and PUMP2.\n\n"
                    "'Check Changes' Button\n"
                    "   After all of the information is entered, click 'Check Changes' to identify any potetial problems with the input. "
                    "After the changes have been checked, click 'Ok' to submit the changes.\n\n" 
                    "Full Example: \n"
                    "PLC Names: PLC1,PLC2\n"
                    "Sensors: P_TANK,S_PUMP1 S_PUMP2\n"
                    "Actuators:  ,PUMP1 PUMP2\n\n"
                    "After clicking 'Ok', the [CYBERNODE] section of the .cpa file should look like this:\n"
                    ";Name, Sensors,    Actuators\n"
                    "PLC1,  P_TANK\n"
                    "PLC2,  S_PUMP1 S_PUMP2,    PUMP1 PUMP2")

            windowTitle = "Help for Re-Assigning CyberNodes"
            newWindow=CreateHelpWindow(text, windowTitle)
            if newWindow.exec_():
                pass
        ### button CHECK
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check Changes')
        self.button_check.clicked.connect(updateChanges)
        ### buttons ok/cancel
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.addButton(self.button_check, QDialogButtonBox.ActionRole)
        ### help button
        self.helpButton = QtWidgets.QPushButton()
        self.helpButton.setText('?')
        self.helpButton.clicked.connect(callHelpWindow)
        #createHelpWindow(self.cpa_dict))
        #self.button_box.addButton(self.helpButton, QDialogButtonBox.ActionRole)
        # def callHelpWindow (self):
        #     newHelpWindow = createHelpWindow(self.cpa_dict)
        #     if newHelpWindow.exec_():
        #         pass
        ### QApplication::setStyle()?? enforce style across different operating systems
        ## layout of the dialog
        outerLayout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QVBoxLayout()
        buttonLayout = QtWidgets.QHBoxLayout()
        #layout.setSpacing(0)
        myFont = QtGui.QFont()
        myFont.setBold(True)
        #layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.setSpacing(1)
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
        layout.addWidget(self.warningtxt)
        buttonLayout.addWidget(self.button_check) 
        buttonLayout.addWidget(self.button_box)
        buttonLayout.addWidget(self.helpButton)
        ##buttonLayout.setSpacing(3)
        #layout.addWidget(self.button_check)
        outerLayout.addLayout(layout)
        outerLayout.addLayout(buttonLayout)
        self.setLayout(outerLayout)
        ### dialog show
        #self.setLayout(layout)
        self.setWindowTitle("Re-Assign CyberNodes")
        self.resize(600, 350)
        self.setMaximumSize(900, 500)
        # self.setFixedWidth(600)
        # self.setFixedHeight(350)
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
        """Connected to the 'Check Changes' button. 
        Calles parsePLCtext, parseSensortext, and parseActuatortext, and sets the return of each function to their respective lists in the storage class."""
        storage.list_of_new_plcs = self.parsePLCtext()
        print(storage.list_of_new_plcs)
        storage.list_of_new_sensors = self.parseSensortext()
        print(storage.list_of_new_sensors)
        storage.list_of_new_actuators = self.parseActuatortext()
        print(storage.list_of_new_actuators)
        inp2cpaApp.isAltered = True
        print(self.warningNo)
        
    def parsePLCtext(self):
        """Called by the check_changes_func function. 
        Splits the user's 'PLC Names' input between commas, adds the PLCs to a list, and returns the list."""
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
            # if (re.search('_.*_', plc)):
            #     self.warningNo=1
            #     list_of_new_plcs.append(plc)
            # else: 
            #     self.warningNo=0
            #     list_of_new_plcs.append(plc)
        #list_of_new_plcs.append(plc)
        return list_of_new_plcs
    
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
        """Called by the check_changes_func function.
        Splits the user's actuator input by commas, adds the acutators to a list, and returns the list."""
        list_of_new_actuators = []
        text = self.newActuatortxt.text()
        text = text.split(',')
        for actuator in text:
            list_of_new_actuators.append(actuator)
        return list_of_new_actuators



class cyberLinkDialog(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        """Called by the addLinks function. 
        Creates the Create CyberLinks window allowing users to create cyberlinks through the GUI."""
        super(cyberLinkDialog, self).__init__()

        def callHelpWindow (event):
            """Connected to the '?' button.
            Calls CreateHelpWindow to create the 'Help for Creating CyberLinks' window."""
            text = ("Creating CyberLinks\n"
            "   This window assists in creating CyberLinks between source and destination nodes. If CyberLinks have already been """
            "created, the CyberLinks saved from this window will replace the current CyberLinks in the .cpa file.\n\n"
            "'Source Names' Field\n"
            "   Enter the sources into the text field, separated by commas. Sources should not be separated by spaces, "
            "or a comma and a space, as the space will be added to the source name.\n\n"
            "'Destination Names' Field\n"
            "   Enter the destinations into the text field, separated by commas. The destinations should be listed in the same "
            "order as their corresponding sources. Destinations should not be separated by spaces, "
            "or a comma and a space, as the space will be added to the destination name.\n\n"
            "'Sensors' Field\n"
            "   Enter the sensors into the text field, separated by commas. The sensors should be listed in the same "
            "order as their corresponding sources. Sensors should not be separated by spaces, "
            "or a comma and a space, as the space will be added to the source name.\n\n"
            "Example: \n"
            "Source Names: PLC1,PLC1\n"
            "Destination Names: PLC2,SCADA\n"
            "Sensors: P_TANK,P_TANK\n\n"
            "   In the above example, there is a CyberLink from PLC1 to PLC2, sending information collected by the P_TANK sensor, "
            "and a CyberLink from PLC1 to SCADA, also sending information collected the P_TANK sensor.\n\n"
            "   After the changes are submitted by selecting the 'Ok' button, the new .cpa file [CYBERLINKS] section should read:\n"
            ";Source, Destination, Sensors\n"
            "PLC1,  PLC2,   P_TANK\n"
            "PLC1,  SCADA,  P_TANK")
            windowTitle = "Help for Creating CyberLinks"
            newWindow=CreateHelpWindow(text, windowTitle)
            if newWindow.exec_():
                pass

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
        ###Help button
        self.helpButton = QtWidgets.QPushButton()
        self.helpButton.setText('?')
        self.helpButton.clicked.connect(callHelpWindow)

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
        buttonLayout.addWidget(self.helpButton)

        ### Set layouts
        outerLayout.addLayout(layout)
        outerLayout.addLayout(buttonLayout)
        self.setLayout(outerLayout)

        ### Set window properties
        self.setWindowTitle("Create CyberLinks")
        # self.setFixedWidth(600)
        # self.setFixedHeight(350) 
        self.resize(600, 350)
        self.setMaximumSize(900, 500)

    def parseNewSource(self):
        """Called by the link_check function. 
        Seperates the user's input by commas, adds the sources to a list, and returns the list."""
        list_of_sources=[]
        text=self.newSourcetxt.text()
        text=text.replace(' ','')
        text=text.split(',')
        for source in text:
            list_of_sources.append(source)
        return list_of_sources

    def parseNewDestination(self):
        """Called by the link_check function.
        Seperates the user's input by commas, adds the destinations to a list, and returns the list."""
        list_of_destinations=[]
        text=self.newDestinationtxt.text()
        text=text.replace(' ','')
        text=text.split(',')
        for destination in text:
            list_of_destinations.append(destination)
        return list_of_destinations

    def parseNewSensor(self):
        """Called by the link_check function.
        Seperates the user's input by commas, adds the sensors to a list, and returns the list."""
        list_of_sensors=[]
        text=self.newSensortxt.text()
        text=text.split(',')
        for sensor in text:
            list_of_sensors.append(sensor)
        return list_of_sensors

    def link_check(self):
        """Called when the 'Check Changes' button is clicked.
        Calles functions to parse the user's source, destination, and sensor inputs. 
        Sets the lists returned by the function to their respective lists in the storage class."""
        storage.list_of_new_sources = self.parseNewSource()
        storage.list_of_new_destinations = self.parseNewDestination()
        storage.list_of_new_link_sensors = self.parseNewSensor()
        print(storage.list_of_new_sources)
        print(storage.list_of_new_destinations)
        print(storage.list_of_new_link_sensors)
        inp2cpaApp.hasCyberLinks = True

class cyberAttackDialog(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        """Called by the addAttack function.
        Creates the Choose an Attack Type window with buttons to select a type of attack to create."""
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
        self.setWindowTitle("Choose an Attack Type")
        self.setMinimumWidth(800)


    def comm_window(self): ################################## just make it its own class
        """Called when the 'Communication' button is pressed in the Choose an Attack Type window.
        Generates a window for creating a communication CyberAttack."""
        #super(cyberAttackDialog, self).__init__()

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
        """Called when the 'Sensor' button is pressed in the Choose an Attack Type window.
        Generates a window for creating a sensor CyberAttack."""
        pass

    def act_window(self):
        """Called when the 'Actuator' button is pressed in the Choose an Attack Type window.
        Generates a window for creating an actuator CyberAttack."""
        pass

class act_window(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
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
        ####layout
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Enter the target actuator', self.targetTxt)
        layout.addRow('Enter the initial condition', self.initCTxt)
        layout.addRow('Enter the ending condition', self.endCTxt)
        layout.addRow('Enter the attack arguments', self.argTxt)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)
        
class con_window(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
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
        ####layout
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Enter the target link or node (i.e. CTRL01l, CTRL01n)', self.targetTxt)
        layout.addRow('Enter the initial condition', self.initCTxt)
        layout.addRow('Enter the ending condition', self.endCTxt)
        layout.addRow('Enter the attack arguments', self.argTxt)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)
        
class sen_window(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
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
        ####layout
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Enter the target sensor', self.targetTxt)
        layout.addRow('Enter the initial condition', self.initCTxt)
        layout.addRow('Enter the ending condition', self.endCTxt)
        layout.addRow('Enter the attack arguments', self.argTxt)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)

    def con_window(self):
        """Called when the 'Control' button is pressed in the Choose an Attack Type window.
        Generates a window for creating a control CyberAttack."""
        pass