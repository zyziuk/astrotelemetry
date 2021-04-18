from astropy.io import fits
import time
import sys
import PyIndi
import os
import threading
import io
import shutil
sys.path.append('indiclient')
from indiClient import IndiClient


from colour_demosaicing import (
    EXAMPLES_RESOURCES_DIRECTORY,
    demosaicing_CFA_Bayer_bilinear,
    demosaicing_CFA_Bayer_Malvar2004,
    demosaicing_CFA_Bayer_Menon2007,
    mosaicing_CFA_Bayer)


class interceptor(IndiClient):
    def __init__(
        self
    ):
        super(interceptor, self).__init__()

    global blobEvent

    def newBLOB(self, bp):
        print("new BLOB ", bp.name)
        blobEvent.set()

    def interceptCCD1(self):

        # Let's take some pictures
        ccd = "ZWO CCD ASI290MM Mini"
        device_ccd = self.getDevice(ccd)
        while not(device_ccd):
            time.sleep(0.5)
            device_ccd = self.getDevice(ccd)

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
        self.setBLOBMode(PyIndi.B_ALSO, ccd, "CCD1")

        ccd1 = device_ccd.getBLOB("CCD1")
        while not(ccd1):
            time.sleep(0.5)
            ccd1 = device_ccd.getBLOB("CCD1")

        return ccd1


    def saveBlobToFits(self, blob):
        fits = blob.getblobdata()
        f = open('tmp/image.fits', 'wb')
        f.write(fits)
        f.close()
        return 'tmp/image.fits'


    def fits2png(self, fitsFile):
        os.system("fitspng -f logistic -fr 0.3,2 -s 4 " + fitsFile)
        return shutil.move("image.png",fitsFile.replace(".fits",".png"))
        # return fitsFile.replace(".fits",".png")

if __name__ == "__main__":

    interceptor = interceptor()
    interceptor.setServer("localhost", 7624)
    interceptor.connectServer()

    ccd1 = interceptor.interceptCCD1()

    blobEvent = threading.Event()
    
    while (1):
        blobEvent.wait()

        for blob in ccd1:
            print("name: ", blob.name, " size: ", blob.size, " format: ", blob.format)
            fitsFile = interceptor.saveBlobToFits(blob)
            interceptor.fits2png(fitsFile)

        blobEvent.clear()        
        time.sleep(1)
        
    # interceptor.processFits("tmp/M_42_Light_020.fits")



