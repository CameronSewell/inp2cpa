from logging import PlaceHolder
from os import link, remove
import sys
from xml.etree.ElementTree import parse
import PyQt5 as Qt
from PyQt5 import QtCore, QtGui, uic, QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

#graph theory imports
from collections import deque
import math

import re

import wntr
import inp2cpa

cybertopo = {}
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
        self.list_of_targets = []
        self.list_of_icond = []
        self.list_of_econd = []
        self.list_of_arg = []

class network:
    node_net = []
    link_net = []
    prop_set = []

    class links:
    #each link can only have one source and destination, but a list of sensor data to transfer
    #links can additionally (optionally) contain arguments identifying communication protocol(s) in use along this connection
        def __init__(self):
            self.source = ''
            self.destination = ''
            self.sensors = []
            self.protocols = {}
    #nodes have a single name, but a list of sensors and actuators, as well as log of which nodes they themselves connect to
    ## potential future assignment of controls to individual PLC, RTU, and/or HMI devices, with redundant assignments and connections as failsafes?
    class nodes:
        def __init__(self):
            self.id = ''
            self.sensors = []
            self.actuators = []
            self.controls = []
            self.linked_nodes = []

    # total graph diversity (TGD)
    def tgd(self):
        runsumArr = []
        cnt = 0
        for lam in [0.2, 1, 5]:
            runsum = 0
            cnt = 0
            for node in self.node_net:
                #print(node.linked_nodes)
                for node2 in self.node_net:
                    if node != node2:
                        #print(node.id + " to " + node2.id)
                        cnt += 1
                        runsum += self.epd(self, lam, node, node2)
                        
            runsumArr.append(runsum/cnt)
        return runsumArr

    #effective path diversity (epd): 1 here filling for lambda, an experimentally-selected value weighting
    # utility of additional paths. Lower values indicate higher utility of additional paths, and vice versa
    def epd(self, lam, node_S, node_D):
        return 1 - math.exp(-lam*self.pathDiv(self, node_S, node_D))

    # calculate individual path diversity between nodes
    def pathDiv(self, node_S, node_D):
        if(self.node_net.__contains__(node_S) and self.node_net.__contains__(node_D)): 
            ksd = 0
            best = []
            temp_ksd = 999
            p0 = self.find_shortest_path(self, self.node_net, node_S, node_D)
            for path in self.find_all_paths(self, self.node_net, node_S, node_D):
                #find minimum ksd
                if path != p0 and 1-(len(set(p0)^set(path))/len(path)) < temp_ksd: 
                    temp_ksd = 1-(len(set(p0)^set(path))/len(path))
                    best = path
            if len(best) == 0: #no other paths found, 0 path diversity
                #print("Zero path div between " + node_S.id  + " and " + node_D.id)
                ksd = 0
            else:        
                ksd += 1-(len(set(p0)^set(best))/len(best))
            return ksd
        else: 
            print('One or more nodes DNE in network.')
            return 0

    #Code from https://www.python.org/doc/essays/graphs/
    def find_path(self, graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.__contains__(start):
            return None
        for node in graph[start]:
            if node not in path:
                newpath = self.find_path(graph, node, end, path)
                if newpath: return newpath
        return None
    #Code adapted from https://www.python.org/doc/essays/graphs/    
    def find_all_paths(self, graph, start, end, path=[]):
        path = path + [start]
        if start.id == end.id:
            #print(path)
            return [path]
        if not any(x.id == start.id for x in graph): #start in graph:
            return []
        paths = []
        for node in start.linked_nodes:
            nodeObj = next((x for x in graph if x.id == node), None)
            if nodeObj not in path:
                newpaths = self.find_all_paths(self, graph, nodeObj, end, path)
                for newpath in newpaths:
                    if newpath not in paths:
                        paths.append(newpath)
        return paths
    #Code from https://www.python.org/doc/essays/graphs/
    def find_shortest_path(self, graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not any(x.id == start.id for x in graph):
            return None
        shortest = None
        for node in start.linked_nodes:
            nodeObj = next((x for x in graph if x.id == node), None)
            if nodeObj not in path:
                newpath = self.find_shortest_path(self, graph, nodeObj, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest

class importWindow(QtWidgets.QDialog):
    def __init__(self):
        """Opens the Import .inp window to allow the user to select an inp. file."""
        QtWidgets.QMainWindow.__init__(self)
        self.setWindowTitle('INP2CPA - Import .inp')
        self.setFixedHeight(140)
        self.setMinimumWidth(400)
        self.resize(600, 140)
        self.setWhatsThis("Help on widget")
        ### text and input fields
        pathname = QLineEdit('Select .inp file . . .')
        pathname.setStyleSheet('color: gray')
        pathname.setReadOnly(True)
        self.selectBttn = QPushButton('Select .inp')
        self.button_box = QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        
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
                for key in cyberTopo.keys():
                    print(str(key) + " : " + str(cyberTopo[key]) + "\n")
            else:
                pathname.setText('Nothing Imported!')


        ### connect buttons
        self.selectBttn.clicked.connect(importINPfunc)
        self.button_box.accepted.connect(lambda: (self.accept, self.mainWindow()))
        self.button_box.rejected.connect(self.reject)

        ### layout of the dialog
        outerLayout = QtWidgets.QVBoxLayout()
        textLayout = QtWidgets.QVBoxLayout()
        inputLayout = QtWidgets.QHBoxLayout()

        ### add widgets
        inputLayout.addWidget(pathname)
        inputLayout.addWidget(self.selectBttn)
        textLayout.addLayout(inputLayout)
        outerLayout.addLayout(textLayout)
        outerLayout.addWidget(self.button_box)
        self.setLayout(outerLayout)
        
    def mainWindow (self):
        """Linked to the Ok button.
        Creates the main inp2cpaApp window."""
        global cpa_dict
        self.close()
        newinp2cpaApp=inp2cpaApp(cpa_dict)
        if newinp2cpaApp.exec_():
                pass   

class inp2cpaApp(QtWidgets.QDialog):
    isAltered = False
    hasCyberLinks = False 
    hasAttacks = False
    hasSettings = False
    def __init__(self, cpa_dict):
        """Initializes main INP2CPA window, including creating buttons linked to their respective functions. """
        super(inp2cpaApp, self).__init__()
        self.setWindowTitle('INP2CPA - ' + pathName)
        self.cpa_dict = cpa_dict
        self.show()
        self.setMaximumHeight(320)
        
        def parse_dict(self):
            """Called by previewCPAfile. 
            Parses imported .inp file, and creates the base/starting .cpa file from the import, stored in the storage class."""
            if inp2cpaApp.isAltered:
                formatted_string = '[CYBERNODES]\n;Name,\tSensors,\tActuators\n'
                network.node_net = []
                for x in range(len(storage.list_of_new_plcs)):
                    range(len(storage.list_of_new_sensors))
                    range(len(storage.list_of_new_actuators))
                    formatted_string = formatted_string + str(storage.list_of_new_plcs[x]) + ',\t' + str(storage.list_of_new_sensors[x]) + ',\t' + str(storage.list_of_new_actuators[x]) + '\n'
                    tempNode = network.nodes()
                    tempNode.id = str(storage.list_of_new_plcs[x])
                    tempNode.sensors.append(storage.list_of_new_sensors[x])
                    tempNode.actuators.append(storage.list_of_new_actuators[x])
                    
                    # no connected nodes at initialization -- may want to add in future updates
                    network.node_net.append(tempNode)
                network.link_net = []
                if inp2cpaApp.hasCyberLinks:
                    formatted_string  = formatted_string + '[CYBERLINKS]\n;Source,\tDestination,\tSensors\n' 
                    for x in range(len(storage.list_of_new_sources)):
                        range(len(storage.list_of_new_destinations))
                        range(len(storage.list_of_new_link_sensors))
                        formatted_string = formatted_string + str(storage.list_of_new_sources[x]) + ',\t' + str(storage.list_of_new_destinations[x]) + ',\t' + str(storage.list_of_new_link_sensors[x]) + '\n'
                        tempLink = network.links()
                        tempLink.source = str(storage.list_of_new_sources[x])
                        tempLink.destination = str(storage.list_of_new_destinations[x])
                        tempLink.sensors.append(storage.list_of_new_link_sensors[x])
                        for node in network.node_net:
                            if tempLink.source == node.id:
                                node.linked_nodes.append(storage.list_of_new_destinations[x])
                        network.link_net.append(tempLink)
                else:
                    formatted_string  = formatted_string + '[CYBERLINKS]\n;Source,\tDestination,\tSensors\n'   

                if inp2cpaApp.hasAttacks:
                    formatted_string  = formatted_string + '[CYBERATTACKS]\n;Source,\tDestination,\tSensors\n' 
                    for x in range(len(storage.list_of_targets)):
                        formatted_string = formatted_string + str(storage.list_of_targets[x]) + ',\t' + str(storage.list_of_icond[x]) + ',\t' + str(storage.list_of_econd[x]) + ',\t' + str(storage.list_of_arg[x])+ '\n'
                else:
                    formatted_string = formatted_string + '[CYBERATTACKS]\n;Type,\tTarget,\tInit_cond,\tEnd_cond,\tArguments\n'
                
                formatted_string = formatted_string + '[CYBEROPTIONS]\n' + 'verbosity'+ '\t' +'1' +'\n'
                formatted_string = formatted_string + ';what_to_store' + '\t'+'everything'+'\n'
                formatted_string = formatted_string + ';pda_options' + '\t' + '0.5' + '\t' + '0' + '\t' + '20' + '\t' + 'Wagner'
                return formatted_string
            else:
                formatted_string='[CYBERNODES]\n'   
                storage.list_of_new_plcs = []
                storage.list_of_new_sensors = []
                storage.list_of_new_actuators = []
                storage.list_of_targets = []
                storage.list_of_icond = []
                storage.list_of_econd = []
                storage.list_of_arg = []
                network.node_net = []
                for PLCkey in self.cpa_dict.keys():
                    storage.list_of_new_plcs.append(PLCkey)
                    tempNode = network.nodes()
                    tempNode.id = str(PLCkey)
                    formatted_string=formatted_string+ str(PLCkey)+'\t'
                    for dict_entry in self.cpa_dict[PLCkey]:
                        storage.list_of_new_sensors.append(dict_entry[0])
                        storage.list_of_new_actuators.append(dict_entry[1])
                        tempNode.sensors = dict_entry[0]
                        tempNode.actuators = dict_entry[1]
                        network.node_net.append(tempNode)
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
                formatted_string  = formatted_string+'[CYBERLINKS]\n;Source,\tDestination,\tSensors\n' 
                formatted_string = formatted_string+'[CYBERATTACKS]'+'\n'+'[CYBEROPTIONS]'+'\n' + 'verbosity'+'\t'+'1'+'\n'
                formatted_string = formatted_string+'what_to_store' + '\t'+'everything'+'\n'
                formatted_string = formatted_string+'pda_options' + '\t'+'0.5'+'\t'+'0'+'\t'+'20'+'\t'+'Wagner'
                return formatted_string   

        def reassignfunc(self):
            """Connected to the 'Re-Assign CyberNodes' button. 
            This function calls the newPLCDialog function (creates the Re-Assign CyberNodes window)."""
            newPLCDlg=newPLCDialog(cpa_dict)
            if newPLCDlg.exec_():
                pass

        def addLinks(self):
            """Connected to the 'Create CyberLinks' button. 
            This function calls the cyberLinkDialog function (creates the Create CyberLinks window)."""
            newLinkDlg = cyberLinkDialog(cpa_dict)
            if newLinkDlg.exec_():
                pass
        
        def addAttack(self):
            """Connected to the 'Create CyberAttacks' button. 
            This function calls the cyberAttackDialog function (creates the Choose an Attack Type window)."""
            attackDlg = cyberAttackDialog(cpa_dict)
            if attackDlg.exec_():
                pass

        def resCheck(self):
            """Connected to the 'Check Resiliency' button.
            This function calls the cyberResiliencyCheck function (creates the Resiliency Check window)."""
            resilDlg = cyberResiliencyCheck(network)
            if resilDlg.exec_():
                pass
        
        def saveCPAfile(self):
            """Connected to the 'Save .cpa' button. 
            Exports .cpa file to users location of choice."""
            name = str(QtWidgets.QFileDialog.getSaveFileName(None, 'Save File', '.', "(*.cpa)")[0])
            print(name)
            file = open(name,'w')
            #formatted_string = parse_dict(self)
            #print ('formattedString')
            #previewBox.setPlainText(formatted_string)
            nonlocal formatted_string
            text = formatted_string
            file.write(text)
            file.close()

        ### Create buttons and text
        formatted_string = parse_dict(self)
        previewtxt = QLabel('Preview .cpa file:')
        previewBox = QPlainTextEdit(formatted_string)
        previewBox.setReadOnly(True)
        nodesBttn = QPushButton('Re-Assign CyberNodes')
        linksBttn = QPushButton('Create CyberLinks')
        attacksBttn = QPushButton('Create CyberAttacks')
        resilSuggBttn = QPushButton('Resiliency Check')
        saveBttn = QPushButton('Save')
        saveBttn.setDefault(True)
        verticalSpacer = QtWidgets.QSpacerItem(60, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding) 
        
        def updatePreview (self):
            """Called bythe Re-Assign CyberNodes and Create CyberLinks buttons.
            Creates a while loop, checking to see when the main window is refocused, and then updates the .cpa preview text."""
            print ('updatePreview called')
            #temp = False
            #while (temp == False):
            #    temp = previewBox.hasFocus()
                #print (temp)
            previewBox.setFocus()
            #if (temp):
            formatted_string = parse_dict(self)
            #print (formatted_string)
            previewBox.setPlainText(formatted_string)

        ### Connect Buttons
        nodesBttn.clicked.connect(lambda: (reassignfunc(self), updatePreview(self)))
        linksBttn.clicked.connect(lambda: (addLinks(self), updatePreview(self)))
        attacksBttn.clicked.connect(lambda: (addAttack(self), updatePreview(self)))
        resilSuggBttn.clicked.connect(lambda: (print("Test TGD: " + str(network.tgd(network))), updatePreview(self)))
        saveBttn.clicked.connect(saveCPAfile)
        
        ### layout of the dialog
        outerLayout = QtWidgets.QVBoxLayout()
        mainLayout = QtWidgets.QVBoxLayout()
        buttonLayout = QtWidgets.QHBoxLayout()

        ### add to layouts
        mainLayout.addWidget(previewtxt)
        mainLayout.addWidget(previewBox)
        buttonLayout.addWidget(nodesBttn)
        buttonLayout.addWidget(linksBttn)
        buttonLayout.addWidget(attacksBttn)
        buttonLayout.addWidget(resilSuggBttn)
        buttonLayout.addSpacerItem(verticalSpacer)
        buttonLayout.addWidget(saveBttn)
        outerLayout.addLayout(mainLayout)
        outerLayout.addLayout(buttonLayout)
        self.setLayout(outerLayout)

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
    warning=['', 'Warning: Format each cybernode with only one underscore', 'Warning: No PLCs entered','Warning: Invalid sensor names, check prefix formatting requirements']
    def __init__(self, cpa_dict):
        """Called by the reassignfunc function. 
        Creates the Re-Assign CyberNodes window allowing users to reassign cybernodes through the GUI."""
        super(newPLCDialog, self).__init__()
        self.cpa_dict=cpa_dict
        self.setFixedWidth(1200)
        self.setFixedHeight(200)
        ### PLC field
        self.newPLCtxt = QtWidgets.QLineEdit()
        self.newPLCtxt.setMinimumWidth(700)
        f_string = ''
        for x in range(len(storage.list_of_new_plcs)):
                f_string = f_string + str(storage.list_of_new_plcs[x]) + ', '
        f_string = f_string[:-2] #subtract final comma, space
        self.newPLCtxt.setText(f_string)
        ### Sensor field
        self.newSensortxt = QtWidgets.QLineEdit()
        self.newSensortxt.setMinimumWidth(700)
        ### Actuator field
        self.newActuatortxt = QtWidgets.QLineEdit()
        self.newActuatortxt.setMinimumWidth(700)
        ### Warning label
        self.warningtxt = QtWidgets.QLabel(self.warning[self.warningNo])
        self.warningtxt.setStyleSheet("""
        QWidget {
            color: red;}
        """)
        ### Check Changes and Update Warning Label
        def updateChanges (event):
            """Connected to the 'Check Changes' button.
            Calls check_changes_funct and updates the warning text.'"""
            self.check_changes_func()
            self.warningtxt.setText(self.warning[self.warningNo])
        def callHelpWindow (event):
            """Connected to the 'Help' button.
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
        ### help button
        self.helpButton = QtWidgets.QPushButton()
        self.helpButton.setText('Help')
        self.helpButton.clicked.connect(callHelpWindow)

        ## layout of the dialog
        outerLayout = QtWidgets.QVBoxLayout()
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow('Add PLC names seperated by \',\'', self.newPLCtxt)
        layout.addRow('Add sensor groups seperated by a \'  \'' ' sensor lists seperated by \',\'', self.newSensortxt)
        layout.addRow('Add actuator groups seperated by a \'  \'' ' actuator lists seperated by \',\'', self.newActuatortxt)
        layout.addRow('Check changes',self.button_check)
        buttonLayout = QtWidgets.QHBoxLayout()
        buttonLayout.addWidget(self.button_box)
        buttonLayout.addWidget(self.helpButton)
        layout.addWidget(self.warningtxt)
        outerLayout.addLayout(layout)
        outerLayout.addLayout(buttonLayout)


        ### dialog show
        self.setLayout(outerLayout)
        self.setWindowTitle("Re-Assign Cyber Nodes")
        self.setMinimumWidth(800)   

    def check_changes_func(self):
        """Connected to the update_changes function. 
        Calls parsePLCtext, parseActuatortext, and parseSensortext to update warning."""
        network.node_net = []
        storage.list_of_new_plcs = self.parsePLCtext()
        #print(storage.list_of_new_plcs)
        storage.list_of_new_sensors = self.parseSensortext()
        network
        #print(storage.list_of_new_sensors)
        storage.list_of_new_actuators = self.parseActuatortext()
        #print(storage.list_of_new_actuators)
        for node_num in range(len(storage.list_of_new_plcs)):
            temp_node = network.nodes()
            temp_node.id = storage.list_of_new_plcs[node_num]
            temp_node.sensors = storage.list_of_new_sensors[node_num]
            temp_node.actuators =  storage.list_of_new_actuators[node_num]
            temp_node.linked_nodes = []
            network.node_net.append(temp_node)
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
            if(len(plc)!=0): 
                plc = plc.lstrip()
            if (re.search('_.*_', plc)):
                self.warningNo=1
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
                if(len(sensor)!=0): 
                    sensor = sensor.lstrip()
                if (re.search('_.*_', sensor)):
                    tempWarning=1
                    # print ('__ ',tempWarning)
                if not (re.search('^S_', sensor) or re.search('^F_', sensor) or re.search('^P_', sensor) or re.search ('^SE_', sensor)) and len(sensor)!=0:                    
                    tempWarning=3
                    #print('tempWarning set by parseSensor')
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
            if(len(actuator)!=0): 
                actuator = actuator.lstrip()
            list_of_new_actuators.append(actuator)
        return list_of_new_actuators
    
    def parseAttackText(self):
        list_of_targets = []


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
        ##Label
        self.titleTxt = QtWidgets.QLabel('Communication Attack')
        self.titleTxt.setMinimumWidth(350)
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
        self.button_box.accepted.connect(self.comm_check)
        self.button_box.rejected.connect(self.reject)
        ###Check changes
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check changes')
        self.button_check.clicked.connect(self.comm_check)
        ####layout
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        layout.addRow("Communication Attacks", self.titleTxt)
        layout.addRow('Enter the target link (i.e. P_tank1-PLC1)', self.targetTxt)
        layout.addRow('Enter the initial condition', self.initCTxt)
        layout.addRow('Enter the ending condition', self.endCTxt)
        layout.addRow('Enter the attack arguments', self.argTxt)
        layout.addRow('Check Changes',self.button_check)
        layout.addWidget(self.button_box)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)

    def comm_check(self):
        storage.list_of_targets.extend(parseAttacks.parseTarget(self.targetTxt.text()))
        storage.list_of_icond.extend(parseAttacks.parseICond(self.initCTxt.text()))
        storage.list_of_econd.extend(parseAttacks.parseECond(self.endCTxt.text()))
        storage.list_of_arg.extend(parseAttacks.parseArg(self.argTxt.text()))
        print(storage.list_of_targets)
        print(storage.list_of_icond)
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
        self.button_box.accepted.connect(self.act_check)
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
        layout.addWidget(self.button_box)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)

    def act_check(self):
        storage.list_of_targets.extend(parseAttacks.parseTarget(self.targetTxt.text()))
        storage.list_of_icond.extend(parseAttacks.parseICond(self.initCTxt.text()))
        storage.list_of_econd.extend(parseAttacks.parseECond(self.endCTxt.text()))
        storage.list_of_arg.extend(parseAttacks.parseArg(self.argTxt.text()))
        print(storage.list_of_targets)
        print(storage.list_of_icond)
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
        self.button_box.accepted.connect(self.con_check)
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
        layout.addWidget(self.button_box)
        ###show
        self.setLayout(layout)
        self.setWindowTitle("Enter attack information")
        self.setMinimumWidth(500)

    def con_check(self):
        storage.list_of_targets.extend(parseAttacks.parseTarget(self.targetTxt.text()))
        storage.list_of_cond.extend(parseAttacks.parseICond(self.initCTxt.text()))
        storage.list_of_econd.extend(parseAttacks.parseECond(self.endCTxt.text()))
        storage.list_of_arg.extend(parseAttacks.parseArg(self.argTxt.text()))
        print(storage.list_of_targets)
        print(storage.list_of_icond)
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
        self.button_box.accepted.connect(self.sen_check)
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
        layout.addWidget(self.button_box)
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
        storage.list_of_icond.extend(parseAttacks.parseICond(self.initCTxt.text()))
        storage.list_of_econd.extend(parseAttacks.parseECond(self.endCTxt.text()))
        storage.list_of_arg.extend(parseAttacks.parseArg(self.argTxt.text()))
        print(storage.list_of_targets)
        print(storage.list_of_icond)
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

class cyberLinkDialog(QtWidgets.QDialog):
    def __init__(self, cpa_dict):
        """Called by the addLinks function. 
        Creates the Create CyberLinks window allowing users to create cyberlinks through the GUI."""
        super(cyberLinkDialog, self).__init__()

        def callHelpWindow (event):
            """Connected to the 'Help' button.
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
        # ###Check changes
        self.button_check = QtWidgets.QPushButton()
        self.button_check.setText('Check Changes')
        self.button_check.clicked.connect(self.link_check)

        ###Button ok/cancel
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(lambda: (self.link_check(), self.close()))
        self.button_box.rejected.connect(self.reject)
        ###Help button
        self.helpButton = QtWidgets.QPushButton()
        self.helpButton.setText('Help')
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
        network.link_net = []
        for source in range(len(storage.list_of_new_sources)):
            temp_link = network.links()
            temp_link.source = storage.list_of_new_sources[source]
            temp_link.destination = storage.list_of_new_destinations[source]
            temp_link.sensors = storage.list_of_new_link_sensors[source]
            #update internal network tracker at the same time
            #print(storage.list_of_new_sources)
            network.link_net.append(temp_link)
            for node in network.node_net:
                if temp_link.source == node.id:
                    node.linked_nodes.append(storage.list_of_new_destinations[source])

        print(storage.list_of_new_sources)
        print(storage.list_of_new_destinations)
        print(storage.list_of_new_link_sensors)
        inp2cpaApp.hasCyberLinks = True

class cyberResiliencyCheck(QtWidgets.QDialog):
    def __init__(self, network):
        """Called by the addLinks function. 
        Creates the Resiliency Check window allowing users to evaluate cyberlinks and node properties through the GUI for basic resiliency/connectivity properties."""
        super(cyberResiliencyCheck, self).__init__()

        def callHelpWindow (event):
            """Connected to the 'Help' button.
            Calls CreateHelpWindow to create the 'Help for Resliency Checking' window."""
            text = ("Checking Resliency\n"
                "   This window assists in evaluating existing network connections and potential resliency between source and destination nodes."""
                " If CyberLinks have already been """
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
            windowTitle = "Help for Checking Resliency"
            newWindow=CreateHelpWindow(text, windowTitle)
            if newWindow.exec_():
                pass
        print("Test TGD: " + str(network.tgd(network)))
        ###Source field
        self.newSourcetxt = QtWidgets.QLineEdit()
        ###Destination field
        self.newDestinationtxt = QtWidgets.QLineEdit()
        ###Sensor field
        self.newSensortxt = QtWidgets.QLineEdit()
        # ###Check changes
        # self.button_check = QtWidgets.QPushButton()
        # self.button_check.setText('Check Changes')
        # self.button_check.clicked.connect(self.link_check)

        ###Button ok/cancel
        self.button_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(lambda: (self.link_check(), self.close()))
        self.button_box.rejected.connect(self.reject)
        ###Help button
        self.helpButton = QtWidgets.QPushButton()
        self.helpButton.setText('Help')
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
        # buttonLayout.addWidget(self.button_check) 
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

