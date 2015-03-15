# -*- coding: utf-8 -*-
"""
Created on Fri Mar 13 17:18:20 2015

@author: nanda_000
"""

# import ftplib python module and other supporting modules
import ftplib, re, socket
from StringIO import StringIO
from shapely.geometry import Polygon
from shapely.geometry import Point

socket.setdefaulttimeout(None) 


# input directories to visit
data_type = "SIR_SIN_L1"
year_type = "2013"
month_type = "01"

# input polygon
greenlandmask = Polygon([(-9, 84),(-9, 57.25),(-77, 57.25),(-77, 84),(-9, 84)])



try:
    
    
    """
    NAVIGATE TO THE FOLDER SPECIFIED BY THE USER IN THE FTP HOST WEBSITE
    
    """
    # initialise an FTP instance for the ESA FTP website for CryoSat
    cryoftp = ftplib.FTP('science-pds.cryosat.esa.int','cryosat246','tOLPiTWn')
    cryoftp_parent_dir = cryoftp.pwd()
    
    #print "CryoSat DIRECTORIES\n"
    # get directories
    dir_data = []
    cryoftp.dir(dir_data.append)
    #for line in dir_data: print "-", line
    
    #print "\nSARIn DIRECTORIES\n"
    # navigate to cryosat SARIn L1b directory
    cryoftp.cwd(data_type)
    SIN_dir_data = []
    cryoftp.dir(SIN_dir_data.append)
    #for line in SIN_dir_data: print "-", line
        
    #print "\nYEAR DIRECTORIES\n"
    # navigate to year folder, say 2013
    cryoftp.cwd(year_type)
    year_dir_data = []
    cryoftp.dir(year_dir_data.append)
    year2013_dir = cryoftp.pwd()
    #for line in year_dir_data: print "-", line
    
    
    months = ['01','02','03','04','05','06','07','08','09','10','11','12']
    

    
    
    #for monthid in months:
    for month_id in months:
    
        print("\n Processing Month %s" % month_id)
        cryoftp.cwd(month_id)
        month_dir_data = []
        cryoftp.dir(month_dir_data.append)
        #for line in month_dir_data: print "-", line
            
        """
        OBTAIN .DBL FILES EXTENSION USING re MODULE
        
        """
        
        # take month directory data and split into string of individual words
        month_dir_split = " ".join(month_dir_data).split()
        
        # set REGEX match criteria (extension match criteria)
        hdr_extension = re.compile('.*\.HDR$')
        
        """
        LOOP THROUGH *.HDR FILES AND FIND THE START/END LATITUDE AND LONGITUDE
        
        """
        
        # create a list od *.HDR files
        dblfiles_inbb = []
        
        for i in month_dir_split:
            if hdr_extension.match(i):
                dblfiles_inbb.append(i)
        
        prev_digits = -1
        
        maxiter = len(dblfiles_inbb)
#        maxiter = 10
        
        # initialise a list of valid *.HDR files
        valid_files = []
                    
        for idx in range(maxiter):

            
            path = "/{0}/{1}/{2}/{3}".format(data_type,year_type,month_id,dblfiles_inbb[idx])
            
            r = StringIO()
            cryoftp.retrbinary('RETR '+path, r.write)
            
            text =  r.getvalue().translate(None,'\t').split('\n')
            startlat = float(text[60].translate(None,'<>Start_Lat unit=""deg/')[4:])/1000000
            startlon = float(text[61].translate(None,'<>Start_Long unit=""deg/')[4:])/1000000
            stoplat  = float(text[62].translate(None,'<>Stop_Lat unit=""deg/')[4:])/1000000
            stoplon  = float(text[63].translate(None,'<>Stop_Long unit=""deg/')[4:])/1000000
            
            startpoint = Point(startlon,startlat)
            stoppoint = Point(stoplon,stoplat)
            
            if greenlandmask.intersects(startpoint) or greenlandmask.intersects(stoppoint):
                path = path.replace('.HDR','.DBL')
                valid_files.append(path)
                
            print("%s%d/%d" % ("\b"*(prev_digits + 1), idx+1,maxiter)),
            prev_digits = len(str(i))
            
        with open('{0}{1}{2}.txt'.format(year_type,month_id,data_type),"w") as textfile:
            for i in valid_files:
                textfile.write("{0}\n".format(i))
        cryoftp.cwd(year2013_dir)
    
    
    
     
    
        
    
    """
    GRACEFULLY CLOSE THE FTP CLIENT
    
    """
    cryoftp.close()
    
except socket.error,e:
    print 'unable to connect!,%s'%e
    
#except ftplib.all_errors, e:
#    errorcode_string = str(e).split(None,1)





