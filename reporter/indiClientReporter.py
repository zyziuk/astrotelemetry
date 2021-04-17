import PyIndi
import time
from statsReporter import StatsReporter


class IndiClientReporter(PyIndi.BaseClient):
    def __init__(self, StatsReporter):
        super(IndiClientReporter, self).__init__()
        self.reporter = StatsReporter

    def strISState(self, s):
        if (s == PyIndi.ISS_OFF):
            return "Off"
        else:
            return "On"

    def strIPState(self, s):
        if (s == PyIndi.IPS_IDLE):
            return "Idle"
        elif (s == PyIndi.IPS_OK):
            return "Ok"
        elif (s == PyIndi.IPS_BUSY):
            return "Busy"
        elif (s == PyIndi.IPS_ALERT):
            return "Alert"

    def newDevice(self, d):
        pass

    def newProperty(self, p):
        pass

    def removeProperty(self, p):
        pass

    def newBLOB(self, bp):
        blob = bp
        print("name: ", blob.name, " size: ",
              blob.size, " format: ", blob.format)
        # pyindi-client adds a getblobdata() method to IBLOB item
        # for accessing the contents of the blob, which is a bytearray in Python
        fits_file = blob.getblobdata()
        print("fits data type: ", type(fits_file))
        f = open('image.fits', 'wb')
        f.write(fits_file)
        f.close()

    def newSwitch(self, svp):
        for l in svp:
            self.reporter.send_data(self.reporter._formatter(
                svp.name, svp.device, l.name, l.label, self.strISState(l.s)))

    def newNumber(self, nvp):
        for l in nvp:
            self.reporter.send_data(self.reporter._formatter(
                nvp.name, nvp.device, l.name, l.label, l.value))

    def newText(self, tvp):
        for l in tvp:
            self.reporter.send_data(self.reporter._formatter(
                tvp.name, tvp.device, l.name, l.label, l.text))

    def newLight(self, lvp):
        for l in lvp:
            self.reporter.send_data(self.reporter._formatter(
                lvp.name, lvp.device, l.name, l.label, self.strIPState(l.s)))

    def newMessage(self, d, m):
        print("*  New Message for", d.getDeviceName(), ":", d.messageQueue(m))

    def serverConnected(self):
        pass

    def serverDisconnected(self, code):
        pass

    def reportAllIndiProps(self, interval):
        while (True):
            dl = self.getDevices()
            for dev in dl:
                pass
            # Print all properties and their associated values.
            for d in dl:
                lp = d.getProperties()
                for p in lp:
                    if p.getType() == PyIndi.INDI_TEXT:
                        tpy = p.getText()
                        for t in tpy:
                            self.reporter.send_data(self.reporter._formatter(
                                p.getName(), d.getDeviceName(), t.name, t.label, t.text))
                    elif p.getType() == PyIndi.INDI_NUMBER:
                        tpy = p.getNumber()
                        for t in tpy:
                            self.reporter.send_data(self.reporter._formatter(
                                p.getName(), d.getDeviceName(), t.name, t.label, t.value))
                    elif p.getType() == PyIndi.INDI_SWITCH:
                        tpy = p.getSwitch()
                        for t in tpy:
                            self.reporter.send_data(self.reporter._formatter(
                                p.getName(), d.getDeviceName(), t.name, t.label, self.strISState(t.s)))
                    elif p.getType() == PyIndi.INDI_LIGHT:
                        tpy = p.getLight()
                        for t in tpy:
                            self.reporter.send_data(self.reporter._formatter(
                                p.getName(), d.getDeviceName(), t.name, t.label, self.strIPState(t.s)))
                    elif p.getType() == PyIndi.INDI_BLOB:
                        tpy = p.getBLOB()
                        for t in tpy:
                            pass
            time.sleep(interval)
