######################################################################

######################################################################
# uGMRT pipeline. This is the EVLA pipeline modified and tuned for uGMRT data analysis. (Arnab Chakraborty: arnab.phy.personal@gmail.com)

######################################################################
version = "1.5.0"
svnrevision = '12nnn'
date = "2018May01"


# Define location of pipeline
pipepath='/home/arnab/uGMRT_DI_pipeline/'

### Decision making ### 

findbadants = True                          # find bad antennas when True
flagbadants= True                           # find and flag bad antennas when True
findbadchans = True                         # find bad channels within known RFI affected freq ranges when True
flagbadfreq= True                           # find and flag bad channels within known RFI affected freq ranges when True


############

#This is the default time-stamped casa log file, in case we
#    need to return to it at any point in the script
log_dir='logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

maincasalog = casalogger.func_globals['casa']['files']['logfile']

def logprint(msg, logfileout=maincasalog):
    print (msg)
    casalog.setlogfile(logfileout)
    casalog.post(msg)
    casalog.setlogfile(maincasalog)
    casalog.post(msg)
    return

#Create timing profile list and file if they don't already exist
if 'time_list' not in globals():
    time_list = []

timing_file='logs/timing.log'

if not os.path.exists(timing_file):
    timelog=open(timing_file,'w')
else:
    timelog=open(timing_file,'a')
    
def runtiming(pipestate, status):
    '''Determine profile for a given state/stage of the pipeline
    '''
    time_list.append({'pipestate':pipestate, 'time':time.time(), 'status':status})
#    
    if (status == "end"):
        timelog=open(timing_file,'a')
        timelog.write(pipestate+': '+str(time_list[-1]['time'] - time_list[-2]['time'])+' sec \n')
        timelog.flush()
        timelog.close()
        #with open(maincasalog, 'a') as casalogfile:
        #    tempfile = open('logs/'+pipestate+'.log','r')
        #    casalogfile.write(tempfile.read())
        #    tempfile.close()
        #casalogfile.close()
#        
    return time_list

######################################################################

# The following script includes all the definitions and functions and
# prior inputs needed by a run of the pipeline.

time_list=runtiming('startup', 'start')
execfile(pipepath+'GMRT_pipe_startup.py')
time_list=runtiming('startup', 'end')
pipeline_save()

######################################################################

try:

######################################################################

# IMPORT THE DATA TO CASA

    execfile(pipepath+'GMRT_pipe_import.py')

######################################################################

# HANNING SMOOTH (OPTIONAL, MAY BE IMPORTANT IF THERE IS NARROWBAND RFI)

    execfile(pipepath+'GMRT_pipe_hanning.py')

######################################################################

# GET SOME INFORMATION FROM THE MS THAT WILL BE NEEDED LATER, LIST
# THE DATA, AND MAKE SOME PLOTS

    execfile(pipepath+'GMRT_pipe_msinfo.py')

######################################################################

# DETERMINISTIC FLAGGING:
# TIME-BASED: online flags, shadowed data, zeroes, pointing scans, quacking
# CHANNEL-BASED: end 5% of channels of each spw, 10 end channels at
# edges of basebands

    execfile(pipepath+'GMRT_pipe_flagall.py')

######################################################################

# PREPARE FOR CALIBRATIONS
# Fill model columns for primary calibrators

    execfile(pipepath+'GMRT_pipe_calprep.py')

######################################################################

# PRIOR CALIBRATIONS
# Gain curves, opacities, antenna position corrections, 
# requantizer gains (NB: requires CASA 4.1 or later!).  Also plots switched
# power tables, but these are not currently used in the calibration

    execfile(pipepath+'GMRT_pipe_priorcals.py')

#*********************************************************************

# INITIAL TEST CALIBRATIONS USING BANDPASS AND DELAY CALIBRATORS

    execfile(pipepath+'GMRT_pipe_testBPdcals.py')

#*********************************************************************

# IDENTIFY AND FLAG BASEBANDS WITH BAD DEFORMATTERS OR RFI BASED ON
# BP TABLE AMPS. This is commented in the py file so that no flagging is done here for GMRT.

    execfile(pipepath+'GMRT_pipe_flag_baddeformatters.py')

#*********************************************************************

# IDENTIFY AND FLAG BASEBANDS WITH BAD DEFORMATTERS OR RFI BASED ON
# BP TABLE PHASES. This is commented in the py file so that no flagging is done here for GMRT.

    execfile(pipepath+'GMRT_pipe_flag_baddeformattersphase.py')

#*********************************************************************

# FLAG POSSIBLE RFI ON BP CALIBRATOR USING RFLAG

    execfile(pipepath+'GMRT_pipe_checkflag.py')

######################################################################

# DO SEMI-FINAL DELAY AND BANDPASS CALIBRATIONS
# (semi-final because we have not yet determined the spectral index
# of the bandpass calibrator)

    execfile(pipepath+'GMRT_pipe_semiFinalBPdcals1.py')
    
######################################################################

# Use flagdata again on calibrators

    execfile(pipepath+'GMRT_pipe_checkflag_semiFinal.py')

######################################################################

# RE-RUN semiFinalBPdcals.py FOLLOWING rflag

    execfile(pipepath+'GMRT_pipe_semiFinalBPdcals2.py')

######################################################################

# Use flagdata again on calibrators

    execfile(pipepath+'GMRT_pipe_checkflag_semiFinal2.py')

######################################################################


# RE-RUN semiFinalBPdcals.py FOLLOWING rflag

    execfile(pipepath+'GMRT_pipe_semiFinalBPdcals3.py')

######################################################################

# DETERMINE SOLINT FOR SCAN-AVERAGE EQUIVALENT

    execfile(pipepath+'GMRT_pipe_solint.py')

######################################################################

# DO TEST GAIN CALIBRATIONS TO ESTABLISH SHORT SOLINT

    execfile(pipepath+'GMRT_pipe_testgains.py')

#*********************************************************************

# MAKE GAIN TABLE FOR FLUX DENSITY BOOTSTRAPPING
# Make a gain table that includes gain and opacity corrections for final
# amp cal, for flux density bootstrapping

    execfile(pipepath+'GMRT_pipe_fluxgains.py')

######################################################################

# FLAG GAIN TABLE PRIOR TO FLUX DENSITY BOOTSTRAPPING
# NB: need to break here to flag the gain table interatively, if
# desired; not included in real-time pipeline

    execfile(pipepath+'GMRT_pipe_fluxflag.py')

#*********************************************************************

# DO THE FLUX DENSITY BOOTSTRAPPING -- fits spectral index of
# calibrators with a power-law and puts fit in model column

    execfile(pipepath+'GMRT_pipe_fluxboot.py')

######################################################################

# MAKE FINAL CALIBRATION TABLES

    execfile(pipepath+'GMRT_pipe_finalcals.py')

######################################################################

# APPLY ALL CALIBRATIONS AND CHECK CALIBRATED DATA

    execfile(pipepath+'GMRT_pipe_applycals.py')

######################################################################

# NOW RUN ALL CALIBRATED DATA (INCLUDING TARGET) THROUGH rflag

    execfile(pipepath+'GMRT_pipe_targetflag.py')

######################################################################

# CALCULATE DATA WEIGHTS BASED ON ST. DEV. WITHIN EACH SPW

    execfile(pipepath+'GMRT_pipe_statwt.py')

######################################################################

# MAKE FINAL UV PLOTS

    execfile(pipepath+'GMRT_pipe_plotsummary.py')

######################################################################

# COLLECT RELEVANT PLOTS AND TABLES

    execfile(pipepath+'GMRT_pipe_filecollect.py')

######################################################################

# WRITE WEBLOG

    execfile(pipepath+'GMRT_pipe_weblog.py')

######################################################################

# Quit if there have been any exceptions caught:

except KeyboardInterrupt, keyboardException:
    logprint ("Keyboard Interrupt: " + str(keyboardException))
except Exception, generalException:
    logprint ("Exiting script: " + str(generalException))
