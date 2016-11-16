import json
import os, os.path, optparse,sys

def get_data_ee(config):
    import ee_download
    return ee_download.download(config)
    
def get_data_peps(config):
    import peps_download
    return peps_download.download(config)


def main():
    
    ###########################################################################
    class OptionParser (optparse.OptionParser):
     
        def check_required (self, opt):
          option = self.get_option(opt)
     
          # Assumes the option's 'default' is set to None!
          if getattr(self.values, option.dest) is None:
              self.error("%s option not supplied" % option)
    ###########################################################################    
    
    #==================
    #parse command line
    #==================
    if len(sys.argv) == 1:
        prog = os.path.basename(sys.argv[0])
        print '      '+sys.argv[0]+' [options]'
        print "     Aide : ", prog, " --help"
        print "        ou : ", prog, " -h"
        sys.exit(-1)
    else :
        usage = "usage: %prog [options] "
        parser = OptionParser(usage=usage)
        parser.add_option("-c","--config",dest="config",action="store",type="string",\
                help = "config file", default=None)
        (options, args) = parser.parse_args()
    
    if options.config==None:
        print("Error no config file, stopping")
        return 1

    print("CONFIG FILE: "+options.config)
    json_data=open(options.config).read()
    config = json.loads(json_data)
    
    if(config["backend"]=="ee" or config["backend"]=="EE" or 
            config["backend"]=="earthengine" or config["backend"]=="EarthEngine"):
        print("BACKEND Earth Engine")
        get_data_ee(config)
              
    elif(config["backend"]=="peps" or config["backend"]=="PEPS"):
        print("BACKEND: PEPS")
        get_data_peps(config)
        
    else:
        print("ERROR: unknown backend")
        return 1
    
    return 

if __name__ == "__main__":
    main()