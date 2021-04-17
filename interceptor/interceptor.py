from PIL import Image
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
import time
import sys
sys.path.append('indiclient')
from indiClient import IndiClient
import PyIndi
import threading


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


    def processFits(self, data = None):
        
        # hdul = fits.open("image.fits")
        # hdul.info()
        # hdul.close()

        # data = fits.getdata("image.fits", ext=0)
        # print(data.shape)

        # # If nothing is there try the second one
        # if data is None:
        #     data = fits.open("image.fits")[1].data

        # vmin = 0
        # vmax = 2

        # # Scale data to range [0, 1]
        # data = (data - vmin)/(vmax - vmin)
        # # Convert to 8-bit integer
        # data = (255*data).astype(np.uint8)
        # # Invert y axis
        # data = data[::-1, :]

        # # Create image from data array and save as jpg
        # image = Image.fromarray(data, 'L')
        # imagename = "image.fits".replace('.fits', '.jpg')
        # image.save(imagename)
        pass

if __name__ == "__main__":

    interceptor = interceptor()
    interceptor.setServer("localhost", 7624)
    interceptor.connectServer()

    ccd1 = interceptor.interceptCCD1()

    blobEvent = threading.Event()
    
    while (1):
        blobEvent.wait()
        print("dupa")

        for blob in ccd1:
            print("name: ", blob.name, " size: ", blob.size, " format: ", blob.format)
            fits = blob.getblobdata()
            print("fits data type: ", type(fits))
            interceptor.processFits(fits)

        blobEvent.clear()        
        time.sleep(1)
        

