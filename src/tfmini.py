# Read from tfmini sensor and post to networktable
from networktables import NetworkTables
import serial

ser = serial.Serial("/dev/ttyUSB0", 115200)
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

                print('(', distance, ',', strength, ')')
                ser.reset_input_buffer()

if __name__ == "__main__":
    try:
        if ser.is_open == False:
            ser.open()
        runForever()
    except KeyboardInterrupt:   # Ctrl+C
        if ser != None:
            ser.close()
    