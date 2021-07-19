# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 14:27:25 2020

@author: dionisis
"""

# import sys
import wntr
import wntr.network.controls as controls

# import argparse

# welcome = "INP2CPA tool"
# parser = argparse.ArgumentParser(description=welcome)
# parser.parse_args()


def cyberControlRead(inp_path):
    """cyberControlRead(inp_path) -> cyberTopology
    
    Reads the predefined epanet controls from the inp_path (input file path) using wntr, and initializes
    a number of variables and conditions. Returns the cyber topology dictionary, which contains a name-indexed list
    of data and sub-lists related to the various components and key properties of the topology."""
    # Read the predefined epanet controls. Also initialize some default inputs
    wn=wntr.network.WaterNetworkModel(inp_path)
    ctrls=wn.control_name_list
    # Dicts with keys CONTROLNAMES
    ctrl_orig_names={'ctrl'+str(i):x for i,x in enumerate(ctrls)}
    ctrl_ID=[x for i,x in enumerate(ctrl_orig_names)] ### THIS IS WHERE IT STARTS LOOKING THROUGH ctrls
    ctrldescr={'ctrl'+str(i):wn.get_control(x).__str__() for i,x in enumerate(ctrls)}
    ctrl_priority={'ctrl'+str(i):wn.get_control(x).priority.__str__() for i,x in enumerate(ctrls)}
    # conditions can be single expression, two and()_conditions , two or()_conditions
    # for single expression conditions
    conditions={'ctrl'+str(i):wn.get_control(x)._condition for i,x in enumerate(ctrls)}
    actions_list={'ctrl'+str(i):wn.get_control(x)._then_actions for i,x in enumerate(ctrls)}
    sensors={ctrl_x:[conditions[ctrl_x]._source_obj.name] for i,ctrl_x in enumerate(ctrldescr.keys()) if isinstance(conditions[ctrl_x], controls.TankLevelCondition) or isinstance(conditions[ctrl_x],controls.ValueCondition) }
    simtimes={ctrl_x:['SimTimeStep'] for i,ctrl_x in enumerate(ctrldescr) if isinstance(conditions[ctrl_x],wntr.network.controls.SimTimeCondition)}
    # sensor attributes
    sensor_attributes={ctrl_x:[conditions[ctrl_x]._source_attr] for i,ctrl_x in enumerate(sensors.keys()) if isinstance(conditions[ctrl_x],wntr.network.controls.TankLevelCondition) or isinstance(conditions[ctrl_x],controls.ValueCondition) }
    sensor_placement={ctrl_x:[conditions[ctrl_x]._source_obj.name] for i,ctrl_x in enumerate(sensors.keys()) if isinstance(conditions[ctrl_x],wntr.network.controls.TankLevelCondition) or isinstance(conditions[ctrl_x],controls.ValueCondition) }
    sensor_placement_type={ctrl_x:[conditions[ctrl_x]._source_obj.node_type] for i,ctrl_x in enumerate(sensors.keys()) if isinstance(conditions[ctrl_x],wntr.network.controls.TankLevelCondition) or isinstance(conditions[ctrl_x],controls.ValueCondition)}
    sensor_threshold={ctrl_x:[conditions[ctrl_x]._threshold] for i,ctrl_x in enumerate(sensors.keys()) if isinstance(conditions[ctrl_x],wntr.network.controls.TankLevelCondition) or isinstance(conditions[ctrl_x],controls.ValueCondition)}
    simtime_signature={ctrl_x:[conditions[ctrl_x]._threshold] for i,ctrl_x in enumerate(conditions) if isinstance(conditions[ctrl_x],wntr.network.controls.SimTimeCondition) }
    sensor_relation={ctrl_x:[conditions[ctrl_x]._relation.__str__()] for i,ctrl_x in enumerate(sensors.keys()) if isinstance(conditions[ctrl_x],wntr.network.controls.TankLevelCondition) or isinstance(conditions[ctrl_x],controls.ValueCondition)}
    simtime_relation={ctrl_x:[conditions[ctrl_x]._relation.__str__()] for i,ctrl_x in enumerate(conditions) if isinstance(conditions[ctrl_x],wntr.network.controls.SimTimeCondition)}
    # for double expression conditions
    boolean_operator={}
    for i,ctrl_x in enumerate(ctrldescr.keys()):
        # for OrConditions     ###for loop is iterating key value pairs  1, ctrl1 2, ctrl2 .....ect.
        if isinstance(conditions[ctrl_x],wntr.network.controls.OrCondition) or isinstance(conditions[ctrl_x],wntr.network.controls.AndCondition):
            if isinstance(conditions[ctrl_x],wntr.network.controls.OrCondition):
                boolean_operator[ctrl_x]='or'
            elif isinstance(conditions[ctrl_x],wntr.network.controls.AndCondition):
                boolean_operator[ctrl_x]='and'
            tempSlist=[]
            tempTlist=[]
            tempAttrlist=[]
            tempPlacelist=[]
            tempPlaceTypelist=[]
            tempThreshlist=[]
            tempSignlist=[]
            tempRelatlist=[]
            tempSimRellist=[]
            if isinstance(conditions[ctrl_x]._condition_1,wntr.network.controls.TankLevelCondition):
                tempSlist.append('S'+conditions[ctrl_x]._condition_1._source_obj.name)
                tempAttrlist.append(conditions[ctrl_x]._condition_1._source_attr)
                tempPlacelist.append(conditions[ctrl_x]._condition_1._source_obj.name)
                tempPlaceTypelist.append(conditions[ctrl_x]._condition_1._source_obj.node_type)
                tempThreshlist.append(conditions[ctrl_x]._condition_1._threshold)
                tempRelatlist.append(conditions[ctrl_x]._condition_1._relation.__str__())
            elif isinstance(conditions[ctrl_x]._condition_1,wntr.network.controls.SimTimeCondition):
                tempTlist.append('SimTimeStep')
                tempSignlist.append(conditions[ctrl_x]._condition_1._threshold)
                tempSimRellist.append(conditions[ctrl_x]._condition_1._relation.__str__())
            ### Second argument
            if isinstance(conditions[ctrl_x]._condition_2,wntr.network.controls.TankLevelCondition):
                tempSlist.append('S'+conditions[ctrl_x]._condition_2._source_obj.name)
                tempAttrlist.append(conditions[ctrl_x]._condition_2._source_attr)
                tempPlacelist.append(conditions[ctrl_x]._condition_2._source_obj.name)
                tempPlaceTypelist.append(conditions[ctrl_x]._condition_2._source_obj.node_type)
                tempThreshlist.append(conditions[ctrl_x]._condition_2._threshold)
                tempRelatlist.append(conditions[ctrl_x]._condition_2._relation.__str__())
            elif isinstance(conditions[ctrl_x]._condition_2,wntr.network.controls.SimTimeCondition):
                tempTlist.append('SimTimeStep')
                tempSignlist.append(conditions[ctrl_x]._condition_2._threshold)
                tempSimRellist.append(conditions[ctrl_x]._condition_2._relation.__str__())
            if tempSlist:
                sensors[ctrl_x]=list(tempSlist)
                sensor_attributes[ctrl_x]=list(tempAttrlist)
                sensor_placement[ctrl_x]=list(tempPlacelist)
                sensor_placement_type[ctrl_x]=list(tempPlaceTypelist)
                sensor_threshold[ctrl_x]=list(tempThreshlist)
                sensor_relation[ctrl_x]=list(tempRelatlist)
            if tempTlist:
                simtimes[ctrl_x]=list(tempTlist)
                simtime_signature[ctrl_x]=list(tempSignlist)
                simtime_relation[ctrl_x]=list(tempSimRellist)
    
    # actions_list contains action objects in list form, double comprehension ###pulling the link from ctrls
    actuators={ctrl_x:[z._target_obj.name for z in actions_list[ctrl_x]] for i,ctrl_x in enumerate(ctrldescr)}
    action_attribute={ctrl_x:[z._attribute for z in actions_list[ctrl_x]] for i,ctrl_x in enumerate(ctrldescr)}
    action_value={ctrl_x:[z._value for z in actions_list[ctrl_x]] for i,ctrl_x in enumerate(ctrldescr)}
    actuator_element={ctrl_x:[z._target_obj.name for z in actions_list[ctrl_x]] for i,ctrl_x in enumerate(ctrldescr)}
    actuator_element_type={ctrl_x:[z._target_obj.link_type for z in actions_list[ctrl_x]] for i,ctrl_x in enumerate(ctrldescr)}
    plcs={ctrl_x:'PLC1' for i,ctrl_x in enumerate(ctrldescr)}
    #plcs={ctrl_x:'PLC'+ i for i,ctrl_x in enumerate(ctrldescr)}
    plc_type={ctrl_x:'slave' for i,ctrl_x in enumerate(ctrldescr)}
    
    # define and return dictionary
    cyberTopology={'Control ID': ctrl_ID,
                   'Control Names': ctrl_orig_names,
                   'Control priority' : ctrl_priority,
                   'Control description' : ctrldescr,
                   'Condition expression': boolean_operator,
                   'Sensors' : sensors,
                   'Simtime cond':simtimes,
                   'Sensor attribute' : sensor_attributes,
                   'Sensor placed at' : sensor_placement,
                   'Sensor placed at asset type' : sensor_placement_type,
                   'Sensor relation':sensor_relation,
                   'Sensor threshold':sensor_threshold,
                   'Simtime signature':simtime_signature,
                   'Simtime relation':simtime_relation,
                   'Actuators' : actuators,
                   'Actuator acts on':actuator_element,
                   'Actuator acts on asset type' : actuator_element_type,
                   'Action attribute':action_attribute,
                   'Action attribute new value':action_value,
                   'PLCs':plcs,
                   'PLC Types':plc_type}
    return cyberTopology

def register_plc(cyberTopology, listOfchanges):
    """This function registers new PLCs to the {cyberTopology} dictionary. Returns a new dict.
    The {listOfchanges} contains a list of tuples [(),(),....()]. The tuple at i unpacks to these properties:
    plcName : str, plcType : str of 'slave' or 'auto', toAssets : list of assets names : str =     listOfchanges[i] .
    toAssets means that the new plc is assigned to controls that deals with the assests in the toAsssets list
        """
    
    for elem in listOfchanges:
    # unpack
        plcName, plcType, toAssets = elem
        print(plcName, plcType, toAssets)
        # check controls that reference the assests
        ctrl_subset=[ctrlID for ctrlID in cyberTopology['Control ID'] if toAssets_in_sesnor_loc(ctrlID,cyberTopology,toAssets) or toAssets_in_actuator_loc(ctrlID,cyberTopology,toAssets) ]
        # Take the keys from the subset and seet the plc to plcName, and the type to plcType
        print(ctrl_subset)
        for ctrlID in ctrl_subset:
            cyberTopology['PLCs'][ctrlID]=plcName
            cyberTopology['PLC Types'][ctrlID]=plcType
    
    return cyberTopology


def toAssets_in_sesnor_loc(key_ID,cyberTopology,assets):
        """ Helper local scope action for checking if an asset from a list is referenced within a control's sensors' location"""
        for asset in assets:
            if asset in cyberTopology['Sensor placed at'][key_ID]:
                return True
        return False
    
def toAssets_in_actuator_loc(key_ID,cyberTopology,assets):
    """ Helper local scope action for checking if an asset from a list is referenced within a control's actuators' location"""
    for asset in assets:
        if asset in cyberTopology['Actuator acts on'][key_ID]:
            return True
    return False

def create_topology_cpa_dict(cyberTopology):
    "Converts a cyberTopology object to a cpa file"
    ctrl_ids = cyberTopology['Control ID']
    list_of_plcs=[]
    cpa_dict={}
    for ctrl_id in ctrl_ids:
        plcname=cyberTopology['PLCs'][ctrl_id]
        if plcname not in list_of_plcs:
            list_of_plcs.append(plcname)
            cpa_dict[plcname]=[[],[]]
        sensor=cyberTopology['Sensors'][ctrl_id]
        actuator=cyberTopology['Actuators'][ctrl_id]
        if sensor not in cpa_dict[plcname][0]:
            cpa_dict[plcname][0].append(sensor)
        if actuator not in cpa_dict[plcname][1]:
            cpa_dict[plcname][1].append(actuator)
    return cpa_dict
            
# def main():
#     welcome = "INP2CPA tool"
#     parser = argparse.ArgumentParser(description=welcome)
#     parser.parse_args()
#     script = sys.argv[0]
#     # filename = sys.argv[1]
#     # data = numpy.loadtxt(filename, delimiter=',')
#     # for row_mean in numpy.mean(data, axis=1):
#     #     print(row_mean)
#     print(script)

# if __name__ == '__main__':
#    main()