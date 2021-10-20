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

# CHECKING FLAGGING OF ALL CALIBRATORS
# use rflag mode of flagdata

logprint ("Starting GMRT_pipe_checkflag_semiFinal.py", logfileout='logs/checkflag_semiFinal.log')
time_list=runtiming('checkflag_semiFinal', 'start')
QA2_checkflag_semiFinal='Pass'

logprint ("Checking RFI flagging of all calibrators", logfileout='logs/checkflag_semiFinal.log')

## flux_set_jy this is the flux set by setJy task and 1.5 times this value is clipped here for flux cal ##

default('flagdata') 

for ii in range(len(myampcals)):

    flagdata(vis=ms_active,mode="clip",spw='',field=myampcals[ii], clipminmax=[0,1.5*flux_set_jy[ii]],
        		datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        		action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)



    flagdata(vis=ms_active,mode="tfcrop", datacolumn="corrected", field=myampcals[ii], ntime="120s",
        		timecutoff=5.0, freqcutoff=5.0, timefit="line",freqfit="line",flagdimension="freqtime", 
        		extendflags=False, usewindowstats='both',halfwin=2, extendpols=False,growaround=False,
        		action="apply", flagbackup=True,overwrite=True, writeflags=True)

    flagdata(vis=ms_active,mode="rflag",datacolumn="corrected",field=myampcals[ii], timecutoff=5.0, 
		        freqcutoff=5.0,timefit="poly",freqfit="line",flagdimension="freqtime", extendflags=False,
		        timedevscale=4.0,freqdevscale=4.0,spectralmax=500.0,extendpols=False, growaround=False,
		        flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)

    flagdata(vis=ms_active,mode="extend",spw=flagspw,field=myampcals[ii],datacolumn="corrected",clipzeros=True,
		         ntime="120s", extendflags=False, extendpols=False,growtime=80.0, growfreq=80.0,growaround=False,
		         flagneartime=False, flagnearfreq=True, action="apply", flagbackup=True,overwrite=True, writeflags=True)



for ii in range(len(mypcals)):

    default(visstat)
    stat = visstat(vis=ms_active,axis="amp",field=mypcals[ii],datacolumn="corrected",useflags=False,spw='',
		selectdata=True,antenna='',uvrange="",timerange="",
		correlation='',scan='',array="",observation="",timeaverage=False,
		timebin="0s",timespan="",maxuvwdistance=0.0,disableparallel=None,ddistart=None,
		taql=None,monolithic_processing=None,intent="",reportingaxes="ddid")
    mean = stat['DATA_DESC_ID=0']['mean']

    flagdata(vis=ms_active,mode="clip",spw='',field=mypcals[ii], clipminmax=[0,3*mean],
        		datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
        		action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)



    flagdata(vis=ms_active,mode="tfcrop", datacolumn="corrected", field=mypcals[ii], ntime="120s",
        		timecutoff=5.0, freqcutoff=5.0, timefit="line",freqfit="line",flagdimension="freqtime", 
        		extendflags=False, usewindowstats='both',halfwin=2, extendpols=False,growaround=False,
        		action="apply", flagbackup=True,overwrite=True, writeflags=True)

    flagdata(vis=ms_active,mode="rflag",datacolumn="corrected",field=mypcals[ii], timecutoff=5.0, 
		        freqcutoff=5.0,timefit="poly",freqfit="line",flagdimension="freqtime", extendflags=False,
		        timedevscale=4.0,freqdevscale=4.0,spectralmax=500.0,extendpols=False, growaround=False,
		        flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)

    flagdata(vis=ms_active,mode="extend",spw=flagspw,field=mypcals[ii],datacolumn="corrected",clipzeros=True,
		         ntime="120s", extendflags=False, extendpols=False,growtime=80.0, growfreq=80.0,growaround=False,
		         flagneartime=False, flagnearfreq=True, action="apply", flagbackup=True,overwrite=True, writeflags=True)



#clearstat()

# Until we know what the QA criteria are for this script, leave QA2
# set score to "Pass".


# Now report statistics after initial flagging 
default('flagdata')
vis=ms_active
mode='summary'
spwchan=True
spwcorr=True
basecnt=True
action='calculate'
savepars=False
afterflags = flagdata()
#clearstat()
logprint ("final flags summary", logfileout='logs/checkflag_semiFinal.log')

after_total = afterflags['total']
after_flagged = afterflags['flagged']
logprint ("After flagging the flagged fraction = "+str(after_flagged/after_total), logfileout='logs/checkflag_semiFinal.log')


logprint ("QA2 score: "+QA2_checkflag_semiFinal, logfileout='logs/checkflag_semiFinal.log')
logprint ("Finished GMRT_pipe_checkflag_semiFinal.py", logfileout='logs/checkflag_semiFinal.log')
time_list=runtiming('checkflag_semiFinal', 'end')

pipeline_save()


######################################################################
