#####################################################################################################
#####################################################################################################
# Here goes the licence
#####################################################################################################
#####################################################################################################

import requests
import zipfile
import StringIO
import Image
import os
import numpy as np
import ee
import datetime
import scipy.misc
import scipy.io
import shutil
from tqdm import *

# initialize earth engine
ee.Initialize()

# Band	Use	Wavelength	Resolution
# B1	Aerosols	443nm	60m
# B2	Blue	490nm	10m
# B3	Green	560nm	10m
# B4	Red	665nm	10m
# B5	Red Edge 1	705nm	20m
# B6	Red Edge 2	740nm	20m
# B7	Red Edge 3	783nm	20m
# B8	NIR	842nm	10m
# B8a	Red Edge 4	865nm	20m
# B9	Water vapor	940nm	60m
# B10	Cirrus	1375nm	60m
# B11	SWIR 1	1610nm	20m
# B12	SWIR 2	2190nm	20m

class S2_Grabber:

    def __init__(self):

        #Load the Sentinel-2 ImageCollection.
        self.sentinel2 = ee.ImageCollection('COPERNICUS/S2')

        # collection parameters
        self.startTime = None
        self.endTime = None
        self.geometry = None
        self.size = None
        self.bands = None

        # collection and cube
        self.collection = None
        self.cube = None

    def set_geometry_rectangle(self, x_ul, y_ul , x_lr, y_lr):
        # x_ul y_ul , x_lr y_lr
        self.geometry = ee.Geometry.Rectangle([x_ul, y_ul , x_lr, y_lr])

    def set_startTime(self, year, month, day):
        self.startTime = datetime.datetime(year, month, day)

    def set_endTime(self, year, month, day):
        self.endTime = datetime.datetime(year, month, day)

    def set_size(self, w,h):
        self.size = (w,h)

    def set_bands(self, bands):
        self.bands = []
        for b in bands:
            self.bands.append({'id':b})

    def get_collection_size(self):
        if self.collection is None:
            raise ValueError("Class S1_grabber --> get_collection_size: \n Collection does not exists")
        collection_infos = self.collection.getInfo()
        collection_features = collection_infos["features"]
        return len(collection_features)

    def create_collection(self):
        if self.geometry is None:
            raise ValueError('No geometry specified')

        self.collection = self.sentinel2.filterBounds(self.geometry)

        if self.startTime is not None and self.endTime is not None:
            self.collection = self.collection.filterDate(self.startTime,self.endTime)

    def download(self,
            directory = ".", # directory for saving images temporary or not
            clean_downloads = False,
            create_cube = False,
            ask_confirmation=True,
            print_size=False):

        if self.collection is None:
            raise ValueError("Class S2_grabber --> download method: \n Collection does not exists")

        collection_infos = self.collection.getInfo()
        collection_features = collection_infos["features"]
        collection_size = len(collection_features)

        if ask_confirmation:
            print("Proceed to download ? [yes]/no: ")
            proceed = raw_input().lower()
            if(proceed == 'no'):
                raise ValueError("User interruption, quitting")

        if create_cube:
            if self.size is not None:
                self.cube = []
            else:
                raise ValueError("Cannot create a cube with size set to None --> please use set_size method")

        # iterate over the images
        for i in tqdm(range(collection_size)):

            # crop the image
            image1 = ee.Image(collection_features[i]['id']).clip(self.geometry)

            # get the download URL for the image
            # filter with polarization if needed
            if self.bands is not None:
                path = image1.getDownloadUrl({'bands':self.bands})
            else:
                path = image1.getDownloadUrl()

            # Donwload the image
            req = requests.get(path)

            # filter the zip to get the TIFs inside
            z = zipfile.ZipFile(StringIO.StringIO(req.content))
            tifs = filter(lambda x: x.endswith('.tif'), z.namelist())

            if self.cube is not None and len(self.bands)>1:
                self.temp_cube = []


            # iterate over the TIFs
            for name in tifs:

                p = z.extract(name)
                newp = os.path.join(directory, name)
                shutil.move(p, newp) # move the file to the directory
                p = newp

                # test if filter on the images dimensiosn
                im = Image.open(p)
                im = np.array(im)

                if print_size:
                    print(im.shape)

                if self.size is not None:
                    if im.shape != self.size:
                        os.remove(p) # remove the file
                        continue

                if self.cube is not None:
                    if len(self.bands)>1:
                        self.temp_cube.append(im)
                    else:
                        self.cube.append(im)

                if clean_downloads:
                    os.remove(p) # remove the file

            if self.cube is not None and len(self.bands)>1:
                self.cube.append(self.temp_cube)

        if self.cube is not None:
            self.cube = np.array(self.cube)

    def save_cube(self,filename):
        if self.cube is not None:
            fname = filename.split(".")
            if fname[-1] == "NPZ" or fname[-1]=="npz":
                np.savez(filename, self.cube)
            elif fname[-1] == "NPY" or fname[-1]=="npy":
                np.save(filename, self.cube)
            elif fname[-1] == "MAT" or fname[-1]=="mat":
                scipy.io.savemat(filename, {'data':self.cube})
            else:
                raise ValueError("S2_Grabber --> save_cube: Unknown file extension")
        else:
            raise ValueError("S2_Grabber --> save_cube: no cube to save")
