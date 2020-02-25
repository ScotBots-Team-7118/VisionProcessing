# Read from tfmini sensor and post to networktable
from networktables import NetworkTables
import serial
import json


def readConfig():
    """Read configuration file."""

    configFile = "/boot/frc.json"

    # parse file
    try:
        with open(configFile, "rt", encoding="utf-8") as f:
            j = json.load(f)
    except OSError as err:
        print("could not open '{}': {}".format(configFile, err), file=sys.stderr)
        return False

    # top level must be an object
    if not isinstance(j, dict):
        parseError("must be JSON object")
        return False

    # team number
    team = 7118
    try:
        team = j["team"]
    except KeyError:
        parseError("could not read team number")
        return False

    ntserver = "roborio-7118-frc.local"
    server = False
    # ntmode (optional)
    if "ntmode" in j:
        str = j["ntmode"]
        if str.lower() == "client":
            server = False
        elif str.lower() == "server":
            server = True
        else:
            parseError("could not understand ntmode value '{}'".format(str))
    if server:
        ntserver = '127.0.0.1'
    else:
        ntserver = "roborio-7118-frc.local"
    
    print("ntserver is: " + ntserver)
    return ntserver

ser = serial.Serial("/dev/ttyUSB0", 115200)
ntserver = readConfig()
# NetworkTables.initialize(server='roborio-7118-frc.local')
NetworkTables.initialize(server='127.0.0.1')
gripdata = NetworkTables.getTable('GripVisionData')
gripdata.putNumber("distance", 0)
gripdata.putBoolean("distanceValid", False)

def runForever():
    while True:
        count = ser.in_waiting
        if count > 8:
            recv = ser.read(9)   
            ser.reset_input_buffer() 
            if recv[0] == 0x59 and recv[1] == 0x59:     #python3
                distance = recv[2] + recv[3] * 256
                strength = recv[4] + recv[5] * 256
                # scale from cm to m
                gripdata.putNumber("distance", distance/100)
                if(strength > 100 and strength != 65535 and distance != 0):
                    gripdata.putBoolean("distanceValid", True)
                else:
                    gripdata.putBoolean("distanceValid", False)

                # print('(', distance, ',', strength, ')')
                ser.reset_input_buffer()

if __name__ == "__main__":
    try:
        if ser.is_open == False:
            ser.open()
        runForever()
    except KeyboardInterrupt:   # Ctrl+C
        if ser != None:
            ser.close()
    