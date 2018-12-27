#!/usr/bin/python3
#
# Domoticz Python Plugin for HDL
#
# Author: :
#
from posix import wait
"""
<plugin key="hdl-switch" name="HDL (plugin)" author="Oleksandr Ivantsiv" version="0.1" wikilink="http://www.domoticz.com/wiki/plugins" externallink="https://todo">
    <params>
        <param field="Address" label="IP Address" width="200px" required="true"/>
        <param field="Port" label="Port" width="50px" required="true" default="6000"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import sys
import Domoticz
sys.path.append('/usr/local/lib/python3.5/dist-packages')
sys.path.append('/usr/lib/python3/dist-packages')
#TODO: Fix PATH
sys.path.append('/home/oleksandr/.local/lib/python3.5/site-packages')
import hdlclient


class HdlPlugin:
    
    enabled = False

    def __init__(self):
        try:
            self.unit_to_light = { idx + 1: name for idx, name in enumerate(sorted(hdlclient.lights.keys()))}
             
            self.unit_to_floor_heating = {}
            self.unit_to_temperature = {}
             
            idx = len(self.unit_to_light) + 1
            for name in sorted(hdlclient.floor_heatings.keys()):
                self.unit_to_floor_heating[idx] = name
                idx += 1
                self.unit_to_temperature[idx] = name
                idx += 1
            
        except:
            import traceback
            traceback.print_exc()

    def onStart(self):
        Domoticz.Log("onStart called")

        for x in Devices:
            name = ""
            if Devices[x].Unit in self.unit_to_light:
                name = self.unit_to_light[Devices[x].Unit]
            elif Devices[x].Unit in self.unit_to_floor_heating:
                name = self.unit_to_floor_heating[Devices[x].Unit]
            else:
                name = self.unit_to_temperature[Devices[x].Unit]

        if not len(Devices):
            for unit, name in self.unit_to_light.items():
                Domoticz.Device(Name=name, Unit=unit, Type=17).Create()
                
            
            for unit, name in self.unit_to_floor_heating.items():
                Domoticz.Device(Name=name, Unit=unit, Type=242, Subtype=1).Create()
            
            
            for unit, name in self.unit_to_temperature.items():
                Domoticz.Device(Name=name, Unit=unit, Type=80).Create()
        
        for name in hdlclient.lights:
            hdlclient.lights[name].set_ip_address(Parameters["Address"])
            hdlclient.lights[name].set_udp_port(Parameters["Port"])
            hdlclient.lights[name].update()
            
        for name in hdlclient.floor_heatings:
            hdlclient.floor_heatings[name].set_ip_address(Parameters["Address"])
            hdlclient.floor_heatings[name].set_udp_port(Parameters["Port"])
            hdlclient.floor_heatings[name].update()
        
        self.onHeartbeat()

    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, unit, command, level, hue):
        Domoticz.Log("onCommand called for Unit " + str(unit) + ": Parameter '" + str(command) + "', Level: " + str(level))
        
        if unit in self.unit_to_light:
            name = self.unit_to_light[unit]
            hdlclient.lights[name].execute_op(command.lower())
            if command.lower() == "on":
                Devices[unit].Update(1, '')
            else:
                Devices[unit].Update(0, '')
        elif unit in self.unit_to_floor_heating:
            name = self.unit_to_floor_heating[unit]
            hdlclient.floor_heatings[name].execute_op("on", "normal", int(level), int(level), int(level), int(level))

        return True

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        
        wait_for = []
        for name in self.unit_to_light.values():
            hdlclient.lights[name].update()
            wait_for.append(hdlclient.lights[name])
        
        for name in self.unit_to_floor_heating.values():
            hdlclient.floor_heatings[name].update()
            wait_for.append(hdlclient.floor_heatings[name])
        
        for dev in wait_for:
            dev.wait()
        
        for x in Devices:
            if Devices[x].Type == 17:
                name = self.unit_to_light[Devices[x].Unit]
                status = hdlclient.lights[name].get_status()
                if status["status"] == "on" and Devices[x].nValue != 1:
                    Devices[x].Update(1, '')
                elif status["status"] == "off" and Devices[x].nValue != 0:
                    Devices[x].Update(0, '')
            elif Devices[x].Type == 80:
                name = self.unit_to_temperature[Devices[x].Unit]
                status = hdlclient.floor_heatings[name].get_status()
                if Devices[x].sValue != str(status["current_temp"]):
                    Devices[x].Update(status["current_temp"], str(status["current_temp"]))
            elif Devices[x].Type == 242:
                name = self.unit_to_floor_heating[Devices[x].Unit]
                status = hdlclient.floor_heatings[name].get_status()
                if Devices[x].sValue != str(status["normal_temp"]):
                    Devices[x].Update(status["normal_temp"], str(status["normal_temp"]))


_plugin = HdlPlugin()


def onStart():
    _plugin.onStart()

def onStop():
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return