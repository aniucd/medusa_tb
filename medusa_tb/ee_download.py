

def download(config):
    if(config["satellite"]=="S1" or config["satellite"]=="s1" or config["satellite"]=="Sentinel1" or config["satellite"]=="sentinel1"):    
        print("SATELLITE: S1")
        config["satellite"]="S1"
        import ee_S1
        # create the grabber
        grabber = ee_S1.S1_Grabber()    
    elif(config["satellite"]=="S2" or config["satellite"]=="s2" or config["satellite"]=="Sentinel2" or config["satellite"]=="sentinel2"):
        print("SATELLITE: S2")
        config["satellite"]="S2"
        import ee_S2
        grabber = ee_S2.S2_Grabber()
    else:
        print("ERROR: unknown satellite")       
        return None
    
    # set the geometry
    grabber.set_geometry_rectangle(config["lonmin"], config["latmin"], config["lonmax"],config["latmax"])
    
    # define start and end dates of the time serie
    # s1_grabber.set_start/endTime(year,month,day)
    startDate = config["startDate"].split()
    endDate = config["endDate"].split()
    for i in range(len(startDate)):
        startDate[i] = int(startDate[i])
        endDate[i] = int(endDate[i])
    print("START DATE: "+str(startDate))
    print("END   DATE: "+str(endDate))
    grabber.set_startTime(startDate[0],startDate[1],startDate[2])
    grabber.set_endTime(endDate[0],endDate[1],endDate[2])
    
    if config["satellite"]=="S1":
        # set the orientation of acquisition
        # "DESCENDING" or "ASCENDING" or None, default is None: get everything
        if "orientation" not in config or config["orientation"] is None:
            print("ORIENTATION: None")
        elif config["orientation"]=="ASCENDING" or config["orientation"]=="DESCENDING":
            print("ORIENTATION: "+config["orientation"])        
            grabber.set_orientation(config["orientation"])
        else:
            print("ERROR: unknown orientation")
            return 
            
        # set the polarization
        # "VV" or "VH" or None, default is None: get everything
        if "polarization" not in config or config["polarization"] is None:
            print("POLARIZATION: None")
        elif config["polarization"]=="VV" or config["polarization"]=="VH":
            print("POLARIZATION: "+config["polarization"])
            grabber.set_polarization(config["polarization"])
        else:
            print("ERROR: unknown polarization")
            return
    else:    
    
        if "bands" not in config or config["bands"] is None:
            print("BANDS: None")
            grabber.set_bands(None)    
        else:
            # set the bands to be donwloaded (if None, download all)
            b = config["bands"].split()
            grabber.set_bands(b)    
    

    if "size" not in config or config["size"] is None:
        print("SIZE: None")
    else:
        s = config["size"].split()
        if len(s) is not 2:
            print("ERROR size problem")
            return
        s[0] = int(s[0])
        s[1] = int(s[1])
        print(s)
        # set the size to filter the images
        grabber.set_size(s[0], s[1])
        
    # create collection
    print("Getting collection")
    grabber.create_collection()    
    print("  collection size: " +str(grabber.get_collection_size()))

    cleanDownloads=True
    if "cleanDownloads" in config and not config["cleanDownloads"]:
        cleanDownloads = False
    createCube=True
    if "createCube" in config  and not config["createCube"]:
        createCube= False
    askConfirmation=True
    if "askConfirmation" in config and not config["askConfirmation"]:
        askConfirmation=False

    print("Dowloading data")
    grabber.download(directory=".", clean_downloads=cleanDownloads, create_cube=createCube,ask_confirmation=askConfirmation)
    
    if createCube:
        grabber.save_cube(config["createCubeFilename"])
        return grabber.cube
    
    return None