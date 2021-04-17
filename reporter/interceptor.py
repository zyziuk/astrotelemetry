import time
import matplotlib.pyplot as plt
from astropy.io import fits
import numpy as np
from PIL import Image


class interceptor:
    def __init__(self):
        super(interceptor, self).__init__()

    def take_picture:

        # Let's take some pictures
        ccd="ZWO CCD ASI290MM Mini"
        device_ccd=indiclient.getDevice(ccd)
        while not(device_ccd):
            time.sleep(0.5)
            device_ccd=indiclient.getDevice(ccd)   
        
        ccd_connect=device_ccd.getSwitch("CONNECTION")
        while not(ccd_connect):
            time.sleep(0.5)
            ccd_connect=device_ccd.getSwitch("CONNECTION")
        if not(device_ccd.isConnected()):
            ccd_connect[0].s=PyIndi.ISS_ON  # the "CONNECT" switch
            ccd_connect[1].s=PyIndi.ISS_OFF # the "DISCONNECT" switch
            indiclient.sendNewSwitch(ccd_connect)
        
        ccd_exposure=device_ccd.getNumber("CCD_EXPOSURE")
        while not(ccd_exposure):
            time.sleep(0.5)
            ccd_exposure=device_ccd.getNumber("CCD_EXPOSURE")
        
        # Ensure the CCD simulator snoops the telescope simulator
        # otherwise you may not have a picture of vega
        ccd_active_devices=device_ccd.getText("ACTIVE_DEVICES")
        while not(ccd_active_devices):
            time.sleep(0.5)
            ccd_active_devices=device_ccd.getText("ACTIVE_DEVICES")
        ccd_active_devices[0].text="EQMod Mount"
        indiclient.sendNewText(ccd_active_devices)
        
        # we should inform the indi server that we want to receive the
        # "CCD1" blob from this device
        indiclient.setBLOBMode(PyIndi.B_ALSO, ccd, "CCD1")
        
        ccd_ccd1=device_ccd.getBLOB("CCD1")
        while not(ccd_ccd1):
            time.sleep(0.5)
            ccd_ccd1=device_ccd.getBLOB("CCD1")

        while (True):
            
            print("start")
            hdul = fits.open("image.fits")
            hdul.info()
            hdul.close()


            data = fits.getdata("image.fits", ext=0)
            print(data.shape)

            # If nothing is there try the second one
            if data is None:
                data = fits.open("image.fits")[1].data

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

            print("stop")
            time.sleep(5)
