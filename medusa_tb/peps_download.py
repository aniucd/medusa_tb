#! /usr/bin/env python
# -*- coding: iso-8859-1 -*-
import json
import time
import os, os.path, sys
from datetime import date

def inDict(str,conf):
    if str not in conf or conf[str]== None:
        return False
    return True

def download(config):

    if "location" not in config or config["location"]==None:    
        if (not inDict("lat",config) ) or (not inDict("lon",config)):
            if (not inDict("latmin",config)) or (not inDict("lonmin",config)) or  \
                (not inDict("latmax",config)) or (not inDict("lonmax",config)):
                print "provide at least a point or rectangle"
                sys.exit(-1)
            else:
                geom='rectangle'
        else:
            if (not inDict("latmin",config)) and (not inDict("lonmin",config)) and \
                (not inDict("latmax",config)) and (not inDict("lonmax",config)):
                geom='point'
            else:
                print "please choose between point and rectangle, but not both"
                sys.exit(-1)
                
    else :
        if (not inDict("latmin",config)) and (not inDict("lonmin",config)) and \
                (not inDict("latmax",config)) and (not inDict("lonmax",config)) and \
                (not inDict("lat",config)) and (not inDict("lon",config)):
            geom='location'
        else :
              print "please choose location and coordinates, but not both"
              sys.exit(-1)
              
    if geom=='point':
        query_geom='lat=%f\&lon=%f'%(config["lat"],config["lon"])
    elif geom=='rectangle':
        query_geom='box={lonmin},{latmin},{lonmax},{latmax}'.format(latmin=config["latmin"],latmax=config["latmax"], \
                        lonmin=config["lonmin"],lonmax=config["lonmax"])
    elif geom=='location':
        query_geom="q=%s"%config["location"]
        
    if inDict("startDate",config):
        start_date="-".join(config["startDate"].split())
        if inDict("endDate",config):
            end_date="-".join(config["endDate"].split())
        else:
            end_date=date.today().isoformat()
    
    
    #====================
    # read authentification file
    #====================
    try:
        (email,passwd)=config["auth"].split()
        if passwd.endswith('\n'):
            passwd=passwd[:-1]
    except :
        print "error with password authentification"
        sys.exit(-2)
    
    
    if os.path.exists('search.json'):
        os.remove('search.json')
        
    search_catalog='curl -k -o search.json https://peps.cnes.fr/resto/api/collections/%s/search.json?%s\&startDate=%s\&completionDate=%s\&maxRecords=500'%(config["satellite"],query_geom,start_date,end_date)
    print search_catalog
    os.system(search_catalog)
    time.sleep(5)
    
    # Filter catalog result
    
    with open('search.json') as data_file:    
        data = json.load(data_file)
    
    if 'ErrorCode' in data :
        print data['ErrorMessage']
        sys.exit(-2)
        
    #Sort data
    download_list={}
    
    for i in range(len(data["features"])):    
        prod=data["features"][i]["properties"]["productIdentifier"]
        feature_id=data["features"][i]["id"]
    
        if inDict("orbit",config):
            if prod.find("_R%03d"%config["orbit"])>0:
                download_list[prod]=feature_id
                print prod,data["features"][i]["properties"]["startDate"]
        
        else:
            print prod,data["features"][i]["properties"]["startDate"]
            download_list[prod]=feature_id
    
    #====================
    # Download
    #====================
    
    if not(inDict("noDownload",config)):
        config["noDownload"] = False
        
    
    if not(config["noDownload"]):
        if len(download_list)==0:
            print "No product matches the criteria"
        else:
            for prod in download_list.keys():
    
                if not inDict("writeDir",config):
                    config["writeDir"]=os.getcwd()	
                file_exists= os.path.exists(("%s/%s.SAFE")%(config["writeDir"],prod)) or  os.path.exists(("%s/%s.zip")%(config["writeDir"],prod))
                tmpfile="%s/tmp.tmp"%config["writeDir"]
                print tmpfile
                get_product='curl -o %s -k -u %s:%s https://peps.cnes.fr/resto/collections/%s/%s/download/?issuerId=peps'%(tmpfile,email,passwd,config["satellite"],download_list[prod])
                print get_product
                if (not(config["noDownload"]) and not(file_exists)):
                    os.system(get_product)
                    #check if binary product
    
                    with open(tmpfile) as f_tmp:
                        try:
                            tmp_data=json.load(f_tmp)
                            print "Result is a text file"
                            print tmp_data
                            sys.exit(-1)
                        except ValueError:
                            pass
    
                    os.rename("%s"%tmpfile,"%s/%s.zip"%(config["writeDir"],prod))
                    print "product saved as : %s/%s.zip"%(config["writeDir"],prod)
                elif file_exists:
                    print "%s already exists"%prod
                elif config["noDownload"]:
                    print "no download (-n) option was chosen"
    
    else :
        print "no download (-n) option was chosen"
