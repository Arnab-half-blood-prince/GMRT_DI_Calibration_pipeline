######################################################################
#
# Copyright (C) 2013
# Associated Universities, Inc. Washington DC, USA,
#
# This library is free software; you can redistribute it and/or modify it
# under the terms of the GNU Library General Public License as published by
# the Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
# License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with this library; if not, write to the Free Software Foundation,
# Inc., 675 Massachusetts Ave, Cambridge, MA 02139, USA.
#
# Correspondence concerning VLA Pipelines should be addressed as follows:
#    Please register and submit helpdesk tickets via: https://help.nrao.edu
#    Postal address:
#              National Radio Astronomy Observatory
#              VLA Pipeline Support Office
#              PO Box O
#              Socorro, NM,  USA
#
######################################################################

# The pipeline assumes all files for a single dataset are located in
# the current directory, and that this directory contains only files
# relating to this dataset.

logprint ("Starting GMRT_pipe_startup.py", logfileout='logs/startup.log')
logprint ("SVN revision "+svnrevision, logfileout='logs/startup.log')


import os
import subprocess as sp
import commands
import numpy as np
import re
import time
from time import gmtime, strftime
import casa
import sys
from math import sin, cos, acos, fabs, pi, e, log10
import scipy as scp
import scipy.optimize as scpo
import pickle
import shutil
import shelve
import copy
import string

def interrupt(message=''):
    """Exit if interrupted
    """
    logprint('Keyboard Interrupt')

def pipeline_save(shelf_filename='pipeline_shelf.restore'):
    '''Save the state of the pipeline
    '''
    if not os.path.exists(shelf_filename):
        pipe_shelf = shelve.open(shelf_filename, 'n')
    else:
        pipe_shelf = shelve.open(shelf_filename)

    try:
        keys = [k for k in open(pipepath+'GMRT_pipe_restore.list').read().split('\n') if k]
    except Exception, e:
        logprint ("Problem with opening keys for pipeline restart: "+str(e))

    for key in keys:
        try:
            pipe_shelf[key] = globals()[key]
            key_status = True
        except:
            key_status = False

    pipe_shelf.close()

######## To read property of the data ####

## source ID ## 
def source_id(msfile,field_name):
    msmd.open(msfile)
    field_id = msmd.fieldsforname(field_name)[0]
    return field_id


def getfields(msfile):
	'''get list of field names in the ms'''
	msmd.open(msfile)  
	fieldnames = msmd.fieldnames()
	msmd.done()
	return fieldnames

def getscans(msfile, mysrc):
	'''get a list of scan numbers for the specified source'''
	msmd.open(msfile)
	myscan_numbers = msmd.scansforfield(mysrc)
	myscanlist = myscan_numbers.tolist()
	msmd.done()
	return myscanlist

###################################


logprint ("GMRT prototype pipeline reduction", 'logs/startup.log')
logprint ("version " + version + " created on " + date, 'logs/startup.log')
logprint ("running from path: " + pipepath, 'logs/startup.log')



# Include functions:
# selectReferenceAntenna
# uniq




execfile(pipepath+'GMRT_functions.py')
execfile(pipepath+'lib_GMRTpipeutils.py')

# File names
#
# if SDM_name is already defined, then assume it holds the SDM directory
# name, otherwise, read it in from stdin
#

SDM_name_already_defined = 1
try:
    SDM_name
except NameError:
    SDM_name_already_defined = 0
    SDM_name=raw_input("Enter SDM file name: ")

# Trap for '.ms', just in case, also for directory slash if present:

SDM_name=SDM_name.rstrip('/')
if SDM_name.endswith('.ms'):
    SDM_name = SDM_name[:-3]

msname=SDM_name+'.ms'
# this is terribly non-robust.  should really trap all the inputs from
# the automatic pipeline (the root directory and the relative paths).
# and also make sure that 'rawdata' only occurs once in the string.
# but for now, take the quick and easy route.
if (SDM_name_already_defined):
    msname = msname.replace('rawdata', 'working')

if not os.path.isdir(msname):
    while not os.path.isdir(SDM_name) and not os.path.isdir(msname):
        print SDM_name+" is not a valid SDM directory"
        SDM_name=raw_input("Re-enter a valid SDM directory (without '.ms'): ")
        SDM_name=SDM_name.rstrip('/')
        if SDM_name.endswith('.ms'):
            SDM_name = SDM_name[:-3]
        msname=SDM_name+'.ms'

mshsmooth=SDM_name+'.hsmooth.ms'
if (SDM_name_already_defined):
    mshsmooth = mshsmooth.replace('rawdata', 'working')
ms_spave=SDM_name+'.spave.ms'
if (SDM_name_already_defined):
    ms_spave = ms_spave.replace('rawdata', 'working')

logprint ("SDM used is: " + SDM_name, logfileout='logs/startup.log')

# Other inputs:

#Ask if a a real model column should be created, or the virtual model should be used
realmodel = raw_input("Create the real model column (y/n): ")

if realmodel=="y":
     scratch=True
else:
     scratch=False

myHanning_already_set = 1
try:
    myHanning
except NameError:
    myHanning_already_set = 0
    myHanning = raw_input("Hanning smooth the data (y/n): ")

#if myHanning=="y":
#    ms_active=mshsmooth
#else:
#    ms_active=msname

ms_active=msname

### choosing the target, flux cal and phase cal ####

myfields = getfields(ms_active) ##field names 
stdcals = ['3C48','3C147','3C286','0542+498','1331+305','0137+331']
vlacals = np.loadtxt(pipepath+'vla-cals.list',dtype='string')
myampcals =[]
mypcals=[]
mytargets=[]
for i in range(0,len(myfields)):
	if myfields[i] in stdcals:
		myampcals.append(myfields[i])
	elif myfields[i] in vlacals:
		mypcals.append(myfields[i])
	else:
		mytargets.append(myfields[i])
mybpcals = myampcals

if len(mypcals) == 0:
   print "No phase calibrator found from vla cal list, using flux calibrator as phase calibrator"
   mypcals = myampcals

print "Amplitude caibrators are", myampcals
print "Phase calibrators are", mypcals
print "Target sources are", mytargets


  

### Taking the scans of different calibrators and target ## 

ampcalscans =[]
flux_cal_id = []

for i in range(0,len(myampcals)):
	ampcalscans.extend(getscans(ms_active, myampcals[i]))
        flux_cal_id.append(source_id(ms_active,myampcals[i]))

pcalscans=[]
phase_cal_id = []
for i in range(0,len(mypcals)):
	pcalscans.extend(getscans(ms_active, mypcals[i]))
        phase_cal_id.append(source_id(ms_active,mypcals[i]))

tgtscans=[]
target_field_id = []
for i in range(0,len(mytargets)):
	tgtscans.extend(getscans(ms_active,mytargets[i]))
        target_field_id.append(source_id(ms_active,mytargets[i]))


allscanlist = ampcalscans+pcalscans+tgtscans
all_calibrator_scan_list = ampcalscans+pcalscans
all_cal_id = flux_cal_id + phase_cal_id

flux_cal_scan_str = ','.join([str(ii) for ii in ampcalscans]) 
phase_cal_scan_str = ','.join([str(jj) for jj in pcalscans]) 
target_scan_str = ','.join([str(kk) for kk in tgtscans])
all_cal_scan_str = ','.join([str(pp) for pp in all_calibrator_scan_list]) 

flux_cal_id_str = ','.join([str(ii) for ii in flux_cal_id]) 
phase_cal_id_str = ','.join([str(jj) for jj in phase_cal_id]) 
target_id_str = ','.join([str(kk) for kk in target_field_id])
all_cal_id_str = ','.join([str(pp) for pp in all_cal_id]) 

bpcalscan = ','.join([str(ii) for ii in getscans(ms_active, myampcals[0])])
bpcalid = str(source_id(ms_active, myampcals[0]))

print "Flux calibrator scans:", flux_cal_scan_str
print "Phase calibrator scans:", phase_cal_scan_str	
print "Target  scans:", target_scan_str

############
gmrt_flux_field = flux_cal_id_str
gmrt_flux_scan = flux_cal_scan_str
gmrt_bandpass_field = bpcalid
gmrt_bandpass_scan = bpcalscan
gmrt_delay_field = bpcalid
gmrt_delay_scan = bpcalscan
gmrt_phase_field = phase_cal_id_str
gmrt_phase_scan = phase_cal_scan_str
gmrt_calibrator_field = all_cal_id_str
gmrt_calibrator_scan = all_cal_scan_str
gmrt_target_field = target_id_str
gmrt_target_scan = target_scan_str
############

############

print 'flux field ID',gmrt_flux_field
print 'flux field scan',gmrt_flux_scan
print 'bandpass field ID',gmrt_bandpass_field
print 'bandpass field scan',gmrt_bandpass_scan
print 'delay field ID',gmrt_delay_field
print 'delay field scan',gmrt_delay_scan
print 'phase field ID',gmrt_phase_field
print 'phase field scan',gmrt_phase_scan
print 'all calibrator field ID',gmrt_calibrator_field
print 'all calibrator field scan',gmrt_calibrator_scan
print 'target field ID',gmrt_target_field
print 'target field scan',gmrt_target_scan


# and the auxiliary information

try:
    projectCode
except NameError:
    projectCode = 'Unknown'
try:
    piName
except NameError:
    piName = 'Unknown'
try:
    piGlobalId
except NameError:
    piGlobalId = 'Unknown'
try:
    observeDateString
except NameError:
    observeDateString = 'Unknown'
try:
    pipelineDateString
except NameError:
    pipelineDateString = 'Unknown'


# For now, use same ms name for Hanning smoothed data, for speed.
# However, we only want to smooth the data the first time around, we do
# not want to do more smoothing on restarts, so note that this parameter
# is reset to "n" after doing the smoothing in EVLA_pipe_hanning.py.

logprint ("Finished GMRT_pipe_startup.py", logfileout='logs/startup.log')

