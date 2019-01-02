#!/usr/bin/env python3
##################################
#Edit by Yusin Chen from https://github.com/insarwxw/Sentinel-1_POE_orbit_download
#More information can found from https://qc.sentinel1.eo.esa.int/doc/api/
####################################################################################
#
# 1) the work path should have a text file containing the RAW data with zip list,
#    e.g., raw_list.txt,
#       S1A_IW_SLC__1SSV_20160511T205050_20160511T205117_011216_010F42_F44A.zip
#       S1A_IW_SLC__1SDV_20180101T205116_20180101T205144_019966_022010_1246.zip
#
# 2) run this script: S1_POE_Orbit_Download.py raw_list.txt  
#    A folder with name of "POE" will be created for putting the downloaded EOF files in the work path.
#
# Notes: Python3 should be pre-installed     
##################################
import numpy as np
import datetime
import urllib.request
import ssl
import re
import os
import subprocess
import argparse
import sys
#################################################################################
INTRODUCTION = '''
  Python script for downloading the Sentinel-1 Precise Orbit Ephemerides (POE) data;
  Please make sure the python3 has been pre-installed in your OS env
'''

EXAMPLE = '''EXAMPLES:

  S1_POE_Orbit_Download.py raw_list.txt 

'''    

def cmdLineParse():
    parser = argparse.ArgumentParser(description='Sentinel-1 POE Orbit Data Downloading',\
                                     formatter_class=argparse.RawTextHelpFormatter,\
                                     epilog=INTRODUCTION+'\n'+EXAMPLE)

    parser.add_argument('raw_list',help="text file containing the S1 ZIP list.")

    inps = parser.parse_args()
    return inps

##################################################################################
def main(argv):
    
    work_path = os.getcwd()
    inps = cmdLineParse()
    zip_list = inps.raw_list
    im_list = np.loadtxt(zip_list,dtype=np.str,ndmin=1)
    
    POE_path = work_path+"/POE"
    os.environ['POE_path'] = str(POE_path);

# Judge whether the POE folder is existing 
    if os.path.exists(POE_path):
        print('Already having the POE foloder')
    else:
        os.popen('mkdir $POE_path')

# List the raw list data 
    #im_list=os.popen('ls $RAW_path | grep ^S1.*SAFE$').read().split()

    for im_var in im_list:
        print("Download the POE orbit file for the list Sentinel-1 image:\n", im_var)
        ###############################Read the image acquire time 
        Sensor=im_var[0:3]
        Sence_time=im_var[17:48]
        Sence_name=im_var[17:25]
        
        S_Year=Sence_time[0:4]
        S_Month=Sence_time[4:6]
        S_Day=Sence_time[6:8]
        S_Hour=Sence_time[9:11]
        S_Minute=Sence_time[11:13]
        S_Second=Sence_time[13:15]

        F_Year=Sence_time[16:20]
        F_Month=Sence_time[20:22]
        F_Day=Sence_time[22:24]
        F_Hour=Sence_time[25:27]
        F_Minute=Sence_time[27:29]
        F_Second=Sence_time[29:31]
     
        ##############################Generate the download url

        url_pre='https://qc.sentinel1.eo.esa.int/api/v1/?';
        url_poe='product_type=AUX_POEORB&validity_stop__gt='+S_Year+'-'+S_Month+'-'+S_Day+'T'+S_Hour+':'+S_Minute+':'+S_Second+'&validity_start__lt='+F_Year+'-'+F_Month+'-'+F_Day+'T'+F_Hour+':'+F_Minute+':'+F_Second+'&sentinel1__mission='+Sensor+'&ordering=-creation_date&page_size=1';
        url_download=url_pre+url_poe;
        print(url_download)
        ###############################Download the page_info and get the POE name 
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        up=urllib.request.urlopen(url_download,context=ctx)
        cont=up.read()
        
    
        ###############################Download the POE data 
        pat=re.compile(Sensor+"_OPER.*.EOF");
        pat_mat=pat.search(str(cont));        
        if pat_mat is None:
            print("****The precise oribt data for this image is not available now****")
            continue
        else:    
            mat=pat_mat.group()
            POE_name=mat[0:73]+'.EOF';
            print();print(POE_name);print()
            POE_file=POE_path+'/'+POE_name
            if  os.path.exists(POE_file):
                print("****The orbit file for this scene has been downloaded already****")
                print("*****************************************************************")
                continue
            else:
                dl_yyyy=mat[25:29]
                dl_mm=mat[29:31]
                dl_dd=mat[31:33]
                dl_head='http://aux.sentinel1.eo.esa.int/POEORB/'+dl_yyyy+'/'+dl_mm+'/'+dl_dd+'/'
                dl_url=dl_head+POE_name;
                cmd='wget '+'-P '+POE_path+' '+dl_url+' --no-check-certificate'
                #cmd='wget '+'-P '+POE_path+' '+dl_url+' -O '+Sence_name+'.EOF'+' --no-check-certificate'
                subprocess.call(cmd,shell=True)

###############################################################################

if __name__ == '__main__':
    main(sys.argv[1:])

