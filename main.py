
import string
from typing import List
import numpy as np
import os
import re
import sys
import shutil
import configparser
import psutil
import functools

from pythonosc.dispatcher import Dispatcher
from pythonosc import osc_server
from pythonosc import udp_client


class Config:

    def __init__(self, filepath:str) -> None:
        '''
        Initialise Config object from filepath to config file.
        '''
        # Read configuration file
        self.config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())

        # Check if configuration file exists
        if not os.path.isfile(filepath):
            raise FileNotFoundError("Config file not found at path: " + filepath)

        self.config.read(filepath)

        try:
            # Details of the VRC OSC server
            self.sourceIP = self.config['Defaults']['sourceIP']
            self.sourcePort = int(self.config['Defaults']['sourcePort'])

            # Details of the OSC router to send to
            self.targetIP = self.config['Defaults']['targetIP']
            self.targetPort = int(self.config['Defaults']['targetPort'])

            # The velocity is mapped to a domain between 0.0 and 1.0
            self.minVelocity = float(self.config['Defaults']['minVelocity'])
            self.maxvelocity = float(self.config['Defaults']['maxVelocity'])
        except KeyError as e:
            raise ValueError(f"Configuration file is missing a required key: {e}")
        
        # Velocity proximity detectors
        self.velocityProximityDetectors = self.setupProximityDetectors()

        # HAPTIC DEVICES
        self.hapticDevices = self.setupHapticDevices()

    def setupHapticDevices(self) -> List:
        '''
        Creates HapticDevice objects based on configuration file.
        '''
        config = self.config

        # Regualr expression to search for HapticDevice in section headers
        pattern = re.compile(r'^HapticDevice.*$')

        # Get the list of haptic device names in the configuration file by searching the section definitions
        hapticDeviceNames = Config.getStringsMatchingPattern(config.sections(),pattern)
        
        hapticDevices = []

        for h in hapticDeviceNames:
            
            try:
                hTargetIP = config[h]['targetIP']
                hTargetPort = int(config[h]['targetPort'])
                hMinVelocity =  float(config[h]['minVelocity'])
                hMaxvelocity = float(config[h]['maxVelocity'])
                hCalculationMode = int(config[h]['calculation_mode'])
                houtput_bool    = float(config[h]['output_bool'])
                hVelocityProximityKeys = [s.strip() for s in config[h]['velocityProximityKeys'].split(',')]
                hVelocityProximityDetectors = self.getVelocityProximityDetectorsByKeys(keys=hVelocityProximityKeys)
                hProximityKey = config[h]['proximityKey']
            except KeyError as e:
                raise ValueError(f"Configuration file is missing a required key: {e}")

            hapticDevices.append(HapticDevice(h,
                                              hTargetIP,
                                              hTargetPort,
                                              hVelocityProximityDetectors,
                                              hMinVelocity, 
                                              hMaxvelocity, 
                                              hProximityKey,
                                              hCalculationMode,
                                              houtput_bool
                                              ))
        return hapticDevices

    def setupProximityDetectors(self) -> List:
        '''
        Creates ProximityDetector objects based on configuration file.
        '''
        config = self.config

        # As many as you like, contacts used to locate the contact sender
        keys = [s.strip() for s in config['VelocityProximityDetectors']['parameterKeys'].split(',')]
        # The radius of the contact used for reporting velocity. One per velocity parameter, to scale the velocity appropriately.
        radii = [float(s.strip()) for s in config['VelocityProximityDetectors']['radii'].split(',')]

        if len(radii) != len(keys):
            raise ValueError("Number of proximity detector keys and number of radii must match.")

        proximityDetectors = []
        for i in range(len(keys)):
            proximityDetectors.append(ProximityDetector(keys[i],radii[i]))
        
        return proximityDetectors

    def getVelocityProximityDetectorsByKeys(self, keys:List[str]) -> List:
        '''
        Returns a sublist of the ProximityDetector objects that correspond to the keys.
        '''
        return [p for p in self.velocityProximityDetectors if p.parameterKey in keys]

    def getStringsMatchingPattern(stringList:List[str], pattern:re.Pattern):
        '''
        Return a sublist of strings where each string matches a regex pattern.
        '''
        return [s for s in stringList if pattern.match(s)]



class ProximityDetector:
    '''
    The ProximityDetector class is an abstract representation of a spherical contact receiver that stores the proximity value and can return the relative position of a contact sender.
    '''
    def __init__(self, parameterKey:str, radius:float=1.0):

        self.parameterKey = parameterKey
        self.radius = radius

        self.parameterValue = 0
    
    def getSenderPosition(self) -> float:
        '''
        Return the relative position of a contact sender based on proximity and radius.
        '''

        return (1 - self.parameterValue) * self.radius

class HapticDevice:
    '''
    The HapticDevice class is an abstract representation of the haptic device, its response to a contact sender, and the target server to forward the OSC message to.
    '''
    def __init__(self, name:str, targetIP:str, targetPort:int, velocityProximityDetectors: List[ProximityDetector], minVelocity:float, maxVelocity:float, proximityParameterKey:str, calculation_mode:int, output_bool:float):
        
        # initialise instance variables
        self.name = name
        self.targetIP = targetIP
        self.targetPort = int(targetPort)

        self.senderPositionVector = [0]*len(velocityProximityDetectors)
        self.previousSenderPositionVector = self.senderPositionVector

        self.velocityProximityDetectors = velocityProximityDetectors

        self.minVelocity = minVelocity
        self.maxVelocity = maxVelocity

        self.proximityParameterKey = proximityParameterKey
        self.proximityParameterValue = 0

        # Initialise the OSC client to send to
        self.client = udp_client.SimpleUDPClient(self.targetIP, self.targetPort)

        self.calculation_mode = calculation_mode

        self.output_bool = output_bool
    
    def updateSenderPosition(self) -> None:
        '''
        Update the current estimated position vector from the velocity proximity detectors.
        '''
        self.previousSenderPositionVector = self.senderPositionVector
        self.senderPositionVector = [v.getSenderPosition() for v in self.velocityProximityDetectors]

    def hapticValue(self) -> float:
        '''
        Return a value to forward to the haptic device between 0 and 1. Assuming 0 is no vibration, 1 is maximum vibration.
        '''
        self.updateSenderPosition()
        v = Physics.computeAverageVelocity(self.senderPositionVector, self.previousSenderPositionVector)
        v = Physics.remapValue(v,self.minVelocity, self.maxVelocity, 0, 1)
        v = Physics.constrainValue(v, 0, 1)
        p = Physics.constrainValue(self.proximityParameterValue,0,1)

        match self.calculation_mode:
            case 0:
                value = v * p
            case 1:
                if self.proximityParameterValue > 0:
                    value = v 
                else: 
                    value = 0.0
            case _:
                raise ("Invalid calculation mode")
        
        if self.output_bool > 0:
            value = 1 if value > self.output_bool else 0
        return value

class Physics:
    '''
    A collection of helper functions to compute the physics and value to be sent to the haptic device.
    '''
    def computeAverageVelocity(pos2:List[float], pos1:List[float], dt:float=1.0) -> float:
        '''
        Estimate the average velocity across a vector of relative positions of the contact sender.
        '''
        dxvec = np.subtract(pos2, pos1)
        dxvec = [abs(dx/dt) for dx in dxvec]
        avg = sum(dxvec)/len(dxvec)

        return avg

    def remapValue(v:float, source0:float, source1:float, target0:float, target1:float) -> float:
        '''
        Remap/convert a value from a source domain to a target domain using linear interpolation, where:
        source0 - the start of the source domain 
        source1 - the end of the source domain
        '''

        v = (v - source0)/(source1 - source0) * (target1 - target0) + target0

        return v

    def constrainValue(v:float, minV:float, maxV:float) -> float:
        '''
        Ensure that a value is always at least 'minV' and at 'most maxV'
        '''
        # Limit the value
        if v < minV:
            v = minV
        elif v > maxV:
            v = maxV
        else:
            v = v
        return v


class Server:
    '''
    The Server class determines how OSC messages will be handled and listens for them.
    '''
    def __init__(self, config: Config):
        
        # Initialise an instance of the dispatcher
        self.dispatcher = Dispatcher()

        self.targetIP = config.targetIP
        self.targetPort = config.targetPort
        self.defaultClient = udp_client.SimpleUDPClient(self.targetIP, self.targetPort)

        self.velocityProximityDetectors = config.velocityProximityDetectors
        self.hapticDevices = config.hapticDevices
        
        # Set up handler functions for ProximityDetectors
        for v in self.velocityProximityDetectors:
            address = Server.parameterNameToVRCAddress(v.parameterKey)
            self.dispatcher.map(address, Server.saveParameterValue, v)
        
        # Set up handler functions for HapticDevices.
        for h in self.hapticDevices:
            address = Server.parameterNameToVRCAddress(h.proximityParameterKey)
            self.dispatcher.map(address,Server.computeHapticValueAndSend, h)
        
        self.dispatcher.set_default_handler(self.default_handler)

        # Initialise the OSC listening server
        server = osc_server.ThreadingOSCUDPServer((config.sourceIP, config.sourcePort), self.dispatcher)
        print("Serving on {}".format(server.server_address))

        # Start the listening server
        server.serve_forever()

    # Function to get the VRChat OSC address from a parameter name
    def parameterNameToVRCAddress(parameterName: string) -> string:
        '''
        Get the VRChat OSC parameter address from the parameter key/name.
        '''
        address = f"/avatar/parameters/{parameterName}"
        return address

    # Functions to be passed to the OSC dispatcher to manage how received OSC messages are handled
    def saveParameterValue(address: str, args, value:str) -> None:
        '''
        Handler for received parameter values to be saved to a ProximityDetector object 'v'.
        '''
        # 'v' is a ProximityDetector object
        v = args[0]
        v.parameterValue = float(value)

    def computeHapticValueAndSend(addr, args, value:str) -> None:
        '''
        Handler for received proximity parameter values for proximity to a haptice device object. 
        This handler will also trigger the current velocity of a contact sender to be computed and sent to the target server.
        '''
        # 'h' is a HapticDevice object
        h = args[0]

        # Store the received OSC parameter value in the HapticDevice object
        h.proximityParameterValue = value

        # Calculate the haptic value (vibration magnitude)
        hapticValue = h.hapticValue()

        # Send the haptic value to the target server
        h.client.send_message(addr, hapticValue)

        print(f"{h.name} : Sending OSC to \"{h.client._address}:{h.client._port}\" at address \"{addr}\" : {hapticValue}")
    
    def default_handler(self, addr, *args) -> None:
        
        value = args[-1]  # Assuming the last argument is the value
        self.defaultClient.send_message(addr, value)

def get_config_path():
    # Determine the directory where the executable resides
    exe_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
    config_path = os.path.join(exe_dir, 'Config.ini')

    # Check if the config file exists at the expected location
    if not os.path.exists(config_path):
        # Config file does not exist, copying from internal bundle to the executable directory
        if getattr(sys, 'frozen', False):
            # When running in a frozen state, copy from temporary bundle directory
            internal_config_path = os.path.join(sys._MEIPASS, 'Config.ini')
        else:
            # When not frozen, assume the config file is in the same directory as the script
            internal_config_path = os.path.join(os.path.dirname(__file__), 'Config.ini')
        
        try:
            shutil.copy(internal_config_path, config_path)
            print(f"Config.ini has been copied to {config_path}")
        except Exception as e:
            print(f"Failed to copy Config.ini: {str(e)}")

    return config_path

if __name__ == "__main__":

    # Set the process priority to high
    p = psutil.Process(os.getpid())
    # Set to high priority. Options: psutil.BELOW_NORMAL_PRIORITY_CLASS, psutil.NORMAL_PRIORITY_CLASS, psutil.ABOVE_NORMAL_PRIORITY_CLASS, psutil.HIGH_PRIORITY_CLASS, psutil.REALTIME_PRIORITY_CLASS (Windows)
    p.nice(psutil.HIGH_PRIORITY_CLASS)

    # Get the config file from the current directory

    configFilepath = get_config_path()

    try:
        # Read the configuration settings from the config file
        config = Config(configFilepath)
    except (FileNotFoundError,ValueError) as e:
        print(f"Error: {e}")

    except Exception as e:
        print(f"Unexpected error occurred: {e}")

    try:
        # Set up the server to listen for OSC parameters and forward them to the target server.
        server = Server(config)
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

    os.system("PAUSE")
