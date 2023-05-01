######################################################################

######################################################################
# uGMRT pipeline. This is the EVLA pipeline modified and tuned for uGMRT data analysis. (Arnab Chakraborty: arnab.phy.personal@gmail.com)
# Updated again to make it faster by skiping some commands like flagdata(vis="SDM.ms",mode="summary", action="calculate"); 
# (Sarvesh Mangla: mangla.sarvesh@gmail.com)
######################################################################
version = "1.5.0"
svnrevision = '12nnn'
date = "2018May01"
Pipeline_Fast = True                  # Want to run faster make it True

# Define location of pipeline
#pipepath='/home/arnab/uGMRT_DI_pipeline/'
homepath = os.path.expanduser('~')
pipepath = os.path.join(homepath,'GMRT_DI_Calibration_pipeline/DI_pipeline/uGMRT_DI_calibration_pipeline/')

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

class bcolors:
    BLACK     = '\033[90m'
    RED       = '\033[91m'
    GREEN     = '\033[92m'
    YELLOW    = '\033[93m'
    BLUE      = '\033[94m'
    MAGENTA   = '\033[95m'
    CYAN      = '\033[96m'
    WHITE     = '\033[97m'
    DEFAULT   = '\033[99m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'
    ENDC      = '\033[0m'

if os.path.exists('Pipeline_working.txt'):
    os.remove('Pipeline_working.txt')

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
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_import.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_import.py"+bcolors.ENDC)

######################################################################

# HANNING SMOOTH (OPTIONAL, MAY BE IMPORTANT IF THERE IS NARROWBAND RFI)

    execfile(pipepath+'GMRT_pipe_hanning.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_hanning.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_hanning.py"+bcolors.ENDC)

######################################################################

# GET SOME INFORMATION FROM THE MS THAT WILL BE NEEDED LATER, LIST
# THE DATA, AND MAKE SOME PLOTS

    execfile(pipepath+'GMRT_pipe_msinfo.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_msinfo.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_msinfo.py"+bcolors.ENDC)

######################################################################

# DETERMINISTIC FLAGGING:
# TIME-BASED: online flags, shadowed data, zeroes, pointing scans, quacking
# CHANNEL-BASED: end 5% of channels of each spw, 10 end channels at
# edges of basebands

    execfile(pipepath+'GMRT_pipe_flagall.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_flagall.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_flagall.py"+bcolors.ENDC)

######################################################################

# PREPARE FOR CALIBRATIONS
# Fill model columns for primary calibrators

    execfile(pipepath+'GMRT_pipe_calprep.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_calprep.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_calprep.py"+bcolors.ENDC)

######################################################################

# PRIOR CALIBRATIONS
# Gain curves, opacities, antenna position corrections, 
# requantizer gains (NB: requires CASA 4.1 or later!).  Also plots switched
# power tables, but these are not currently used in the calibration

    execfile(pipepath+'GMRT_pipe_priorcals.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_priorcals.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_priorcals.py"+bcolors.ENDC)

#*********************************************************************

# INITIAL TEST CALIBRATIONS USING BANDPASS AND DELAY CALIBRATORS

    execfile(pipepath+'GMRT_pipe_testBPdcals.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_testBPdcals.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_testBPdcals.py"+bcolors.ENDC)

#*********************************************************************

# IDENTIFY AND FLAG BASEBANDS WITH BAD DEFORMATTERS OR RFI BASED ON
# BP TABLE AMPS. This is commented in the py file so that no flagging is done here for GMRT.

    execfile(pipepath+'GMRT_pipe_flag_baddeformatters.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_flag_baddeformatters.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_flag_baddeformatters.py"+bcolors.ENDC)

#*********************************************************************

# IDENTIFY AND FLAG BASEBANDS WITH BAD DEFORMATTERS OR RFI BASED ON
# BP TABLE PHASES. This is commented in the py file so that no flagging is done here for GMRT.

    execfile(pipepath+'GMRT_pipe_flag_baddeformattersphase.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_flag_baddeformattersphase.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_flag_baddeformattersphase.py"+bcolors.ENDC)

#*********************************************************************

# FLAG POSSIBLE RFI ON BP CALIBRATOR USING RFLAG

    execfile(pipepath+'GMRT_pipe_checkflag.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_checkflag.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_checkflag.py"+bcolors.ENDC)

######################################################################

# DO SEMI-FINAL DELAY AND BANDPASS CALIBRATIONS
# (semi-final because we have not yet determined the spectral index
# of the bandpass calibrator)

    execfile(pipepath+'GMRT_pipe_semiFinalBPdcals1.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_semiFinalBPdcals1.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_semiFinalBPdcals1.py"+bcolors.ENDC)

######################################################################

# Use flagdata again on calibrators

    execfile(pipepath+'GMRT_pipe_checkflag_semiFinal.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_checkflag_semiFinal.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_checkflag_semiFinal.py"+bcolors.ENDC)

######################################################################

# RE-RUN semiFinalBPdcals.py FOLLOWING rflag

    execfile(pipepath+'GMRT_pipe_semiFinalBPdcals2.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_semiFinalBPdcals2.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_semiFinalBPdcals2.py"+bcolors.ENDC)

######################################################################

# Use flagdata again on calibrators

    execfile(pipepath+'GMRT_pipe_checkflag_semiFinal2.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_checkflag_semiFinal2.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_checkflag_semiFinal2.py"+bcolors.ENDC)

######################################################################


# RE-RUN semiFinalBPdcals.py FOLLOWING rflag

    execfile(pipepath+'GMRT_pipe_semiFinalBPdcals3.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_semiFinalBPdcals3.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_semiFinalBPdcals3.py"+bcolors.ENDC)

######################################################################

# DETERMINE SOLINT FOR SCAN-AVERAGE EQUIVALENT

    execfile(pipepath+'GMRT_pipe_solint.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_solint.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_solint.py"+bcolors.ENDC)

######################################################################

# DO TEST GAIN CALIBRATIONS TO ESTABLISH SHORT SOLINT

    execfile(pipepath+'GMRT_pipe_testgains.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_testgains.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_testgains.py"+bcolors.ENDC)

#*********************************************************************

# MAKE GAIN TABLE FOR FLUX DENSITY BOOTSTRAPPING
# Make a gain table that includes gain and opacity corrections for final
# amp cal, for flux density bootstrapping

    execfile(pipepath+'GMRT_pipe_fluxgains.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_fluxgains.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_fluxgains.py"+bcolors.ENDC)

######################################################################

# FLAG GAIN TABLE PRIOR TO FLUX DENSITY BOOTSTRAPPING
# NB: need to break here to flag the gain table interatively, if
# desired; not included in real-time pipeline

    execfile(pipepath+'GMRT_pipe_fluxflag.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_fluxflag.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_fluxflag.py"+bcolors.ENDC)

#*********************************************************************

# DO THE FLUX DENSITY BOOTSTRAPPING -- fits spectral index of
# calibrators with a power-law and puts fit in model column

    execfile(pipepath+'GMRT_pipe_fluxboot.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_fluxboot.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_fluxboot.py"+bcolors.ENDC)

######################################################################

# MAKE FINAL CALIBRATION TABLES

    execfile(pipepath+'GMRT_pipe_finalcals.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_finalcals.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_finalcals.py"+bcolors.ENDC)

######################################################################

# APPLY ALL CALIBRATIONS AND CHECK CALIBRATED DATA

    execfile(pipepath+'GMRT_pipe_applycals.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_applycals.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_applycals.py"+bcolors.ENDC)

######################################################################

# NOW RUN ALL CALIBRATED DATA (INCLUDING TARGET) THROUGH rflag

    execfile(pipepath+'GMRT_pipe_targetflag.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_targetflag.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_targetflag.py"+bcolors.ENDC)

######################################################################

# CALCULATE DATA WEIGHTS BASED ON ST. DEV. WITHIN EACH SPW

    execfile(pipepath+'GMRT_pipe_statwt.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_statwt.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_statwt.py"+bcolors.ENDC)

######################################################################

# MAKE FINAL UV PLOTS

    execfile(pipepath+'GMRT_pipe_plotsummary.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_plotsummary.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_plotsummary.py"+bcolors.ENDC)

######################################################################

# COLLECT RELEVANT PLOTS AND TABLES

    execfile(pipepath+'GMRT_pipe_filecollect.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_filecollect.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_filecollect.py"+bcolors.ENDC)

######################################################################

# WRITE WEBLOG

    execfile(pipepath+'GMRT_pipe_weblog.py')
    Pipe_info = open('Pipeline_working.txt','a')
    Pipe_info.write("\nGMRT_pipe_weblog.py\tDONE")
    Pipe_info.close()
    print(bcolors.GREEN+"Successfully Done >>> GMRT_pipe_weblog.py"+bcolors.ENDC)

######################################################################
    print(bcolors.GREEN+"Pipeline had a good RUN"+bcolors.ENDC)

# Quit if there have been any exceptions caught:

except KeyboardInterrupt, keyboardException:
    logprint ("Keyboard Interrupt: " + str(keyboardException))
except Exception, generalException:
    logprint ("Exiting script: " + str(generalException))
