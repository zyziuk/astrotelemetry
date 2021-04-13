import PyIndi
import time
import sys
import socket
import math
import random
import atexit

def format_measurement_to_str_influx(measure, device, field, label, value):

    if str(type(value)) == "<class 'str'>":
        quotation = "\""
    else:
        quotation = ""

    measure = measure.replace(" ","_").replace(",","_")
    device = device.replace(" ","_").replace(",","_")
    field = field.replace(" ","_").replace(",","_")
    label = label.replace(" ","_").replace(",","_")
    value = str(value).replace(" ","_").replace(",","_")

    data = measure+",astro_device="+device+" "+field+"("+label+")"+"="+quotation+value+quotation
    
    return data.upper()

def strISState(s):
    if (s == PyIndi.ISS_OFF):
        return "Off"
    else:
        return "On"
def strIPState(s):
    if (s == PyIndi.IPS_IDLE):
        return "Idle"
    elif (s == PyIndi.IPS_OK):
        return "Ok"
    elif (s == PyIndi.IPS_BUSY):
        return "Busy"
    elif (s == PyIndi.IPS_ALERT):
        return "Alert"


class StatsReporter:
    def __init__(
        self,
        socket_type,
        socket_address,
        encoding='utf-8',
        formatter=None
    ):
        self._socket_type = socket_type
        self._socket_address = socket_address
        self._encoding = encoding
        self._formatter = formatter
        self.create_socket()

    def create_socket(self):
        try:
            sock = socket.socket(*self._socket_type)
            # no sock.connect
            self._sock = sock
        except socket.error as e:
            pass

    def close_socket(self):
        try:
            self._sock.close()
        except (AttributeError, socket.error) as e:
            pass

    def send_data(self, data):
        try:
            sent = self._sock.sendto(data.encode(self._encoding),self._socket_address)

        except (AttributeError, socket.error) as e:

            # attempt to recreate socket on error
            self.close_socket()
            self.create_socket()


class IndiClient(PyIndi.BaseClient):
    def __init__(self):
        super(IndiClient, self).__init__()
        self.ipadress = "localhost"

    def newDevice(self, d):
        pass

    def newProperty(self, p):
        pass

    def removeProperty(self, p):
        pass
        
    def newBLOB(self, bp):
        pass

    def newSwitch(self, svp):
        for l in svp:
            reporter.send_data(reporter._formatter(svp.name,svp.device,l.name,l.label,strISState(l.s)))

    def newNumber(self, nvp):
        for l in nvp:
            reporter.send_data(reporter._formatter(nvp.name,nvp.device,l.name,l.label,l.value))

    def newText(self, tvp):
        for l in tvp:
            reporter.send_data(reporter._formatter(tvp.name,tvp.device,l.name,l.label,l.text))

    def newLight(self, lvp):
        for l in lvp:
            reporter.send_data(reporter._formatter(lvp.name,lvp.device,l.name,l.label,strIPState(l.s)))

    def newMessage(self, d, m):
        print("*  New Message for",d.getDeviceName(),":", d.messageQueue(m))

    def serverConnected(self):
        pass

    def serverDisconnected(self, code):
        pass


reporter = StatsReporter((socket.AF_INET, socket.SOCK_DGRAM),('localhost', 8094), formatter=format_measurement_to_str_influx)
atexit.register(reporter.close_socket)


indiclient = IndiClient()
indiclient.setServer(indiclient.ipadress, 7624)

time.sleep(60)

indiclient.connectServer()

while (True):
    dl=indiclient.getDevices()
    for dev in dl:
        pass
    # Print all properties and their associated values.
    for d in dl:
        lp=d.getProperties()
        for p in lp:
            if p.getType()==PyIndi.INDI_TEXT:
                tpy=p.getText()
                for t in tpy:
                    reporter.send_data(reporter._formatter(p.getName(),d.getDeviceName(),t.name,t.label,t.text))
            elif p.getType()==PyIndi.INDI_NUMBER:
                tpy=p.getNumber()
                for t in tpy:
                    reporter.send_data(reporter._formatter(p.getName(),d.getDeviceName(),t.name,t.label,t.value))
            elif p.getType()==PyIndi.INDI_SWITCH:
                tpy=p.getSwitch()
                for t in tpy:
                    reporter.send_data(reporter._formatter(p.getName(),d.getDeviceName(),t.name,t.label,strISState(t.s)))
            elif p.getType()==PyIndi.INDI_LIGHT:
                tpy=p.getLight()
                for t in tpy:
                    reporter.send_data(reporter._formatter(p.getName(),d.getDeviceName(),t.name,t.label,strIPState(t.s)))
            elif p.getType()==PyIndi.INDI_BLOB:
                tpy=p.getBLOB()
                for t in tpy:
                    pass
    time.sleep(9)

