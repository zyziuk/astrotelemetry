import sys
sys.path.append('indiclient')
from indiClient import IndiClient
from astropy.io import fits
import time
import PyIndi
import os
import threading
import io
import shutil
import logging



class Interceptor(IndiClient):
    def __init__(self, ccdName, fitsFile, remoteSSHServer, fitspngCmd):
        super(Interceptor, self).__init__()
        logging.basicConfig(format='%(asctime)s [%(filename)s %(module)s %(funcName)s] %(message)s', level=logging.INFO)
        self.logger = logging.getLogger('Interceptor')
        self.ccdName = ccdName
        self.remoteSSHServer = remoteSSHServer
        self.fitsFile = fitsFile
        self.fitspngCmd = fitspngCmd

    def newBLOB(self, bp):
        blobEvent.set()

    def interceptCCD1(self):

        # Let's take some pictures
        device_ccd = self.getDevice(self.ccdName)
        while not(device_ccd):
            time.sleep(0.5)
            device_ccd = self.getDevice(self.ccdName)

        ccd_connect = device_ccd.getSwitch("CONNECTION")
        while not(ccd_connect):
            time.sleep(0.5)
            ccd_connect = device_ccd.getSwitch("CONNECTION")
        if not(device_ccd.isConnected()):
            ccd_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            ccd_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            self.sendNewSwitch(ccd_connect)

        ccd_exposure = device_ccd.getNumber("CCD_EXPOSURE")
        while not(ccd_exposure):
            time.sleep(0.5)
            ccd_exposure = device_ccd.getNumber("CCD_EXPOSURE")

        # Ensure the CCD simulator snoops the telescope simulator
        # otherwise you may not have a picture of vega
        ccd_active_devices = device_ccd.getText("ACTIVE_DEVICES")
        while not(ccd_active_devices):
            time.sleep(0.5)
            ccd_active_devices = device_ccd.getText("ACTIVE_DEVICES")

        ccd_active_devices[0].text = "EQMod Mount"
        self.sendNewText(ccd_active_devices)

        # we should inform the indi server that we want to receive the
        # "CCD1" blob from this device
        self.setBLOBMode(PyIndi.B_ALSO, self.ccdName, "CCD1")

        ccd1 = device_ccd.getBLOB("CCD1")
        while not(ccd1):
            time.sleep(0.5)
            ccd1 = device_ccd.getBLOB("CCD1")

        return ccd1

    def saveBlobToFits(self, blob):
        fits = blob.getblobdata()
        f = open(self.fitsFile, 'wb')
        f.write(fits)
        f.close()

        return self.fitsFile

    def fits2png(self, fitsFile):
        os.system(self.fitspngCmd + " " + fitsFile)

        return shutil.move("image.png", fitsFile.replace(".fits", ".png"))

    def transport(self, pngFile, remote):
        os.system("scp " + pngFile + " " + remote)

    def process(self):
        ccd1 = self.interceptCCD1()

        global blobEvent
        blobEvent = threading.Event()

        while (1):
            blobEvent.wait()

            for blob in ccd1:
                fitsFile = self.saveBlobToFits(blob)
                pngFile = self.fits2png(fitsFile)
                self.logger.info("Transfering %s to %s ...", pngFile, self.remoteSSHServer)
                self.transport(pngFile, self.remoteSSHServer)

            blobEvent.clear()
            time.sleep(1)


if __name__ == "__main__":

    interceptor = Interceptor()
    interceptor.setServer("localhost", 7624)
    interceptor.connectServer()
    interceptor.process()
