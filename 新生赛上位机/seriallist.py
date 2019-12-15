import serial
import serial.tools.list_ports

port_list = list(serial.tools.list_ports.comports())

if len(port_list) <= 0:
    print("The Serial port can't find!")

else:
    for portlist in port_list:
        try:
            port_list_0=list(portlist)
            port_serial = port_list_0[0]
            ser = serial.Serial(port_serial,115200,timeout = 1)
            print("check which port was really used >",port_list_0)
        except BaseException as e:
            print('except:', e)