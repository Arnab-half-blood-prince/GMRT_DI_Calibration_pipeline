
def vislistobs(msfile):
	'''Writes the verbose output of the task listobs.'''
	os.system('rm '+msfile+'.list')
	ms.open(msfile)  
	outr=ms.summary(verbose=True,listfile=msfile+'.list')
	print "A file containing listobs output is saved."
	return outr

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


# this function is for those ms files which is being imported with importgmrt task

def getantlist_import_GMRT(myvis,scanno):   
	msmd.open(myvis)
	antenna_name = msmd.antennasforscan(scanno)
	antlist=[]
	for i in range(0,len(antenna_name)):
		antlist.append(msmd.antennanames(antenna_name[i])[0])
	return antlist

# this function is for those ms files which is being imported with importuvfits task
def getantlist(myvis,scanno):
	msmd.open(myvis)
	antenna_name = msmd.antennasforscan(scanno)
	antlist=[]
	for i in range(0,len(antenna_name)):
                ant_str = msmd.antennastations(antenna_name[i])[0]
                ant_name = ant_str.split(':')[0]  
		antlist.append(ant_name)
	return antlist

def getantid(myvis,scanno):
	msmd.open(myvis)
	antid = msmd.antennasforscan(scanno)
	
	
	return antid


def getnchan(msfile):
	msmd.open(msfile)
	nchan = msmd.nchan(0)
	msmd.done()
	return nchan


def freq_info(ms_file):									
	sw = 0
	msmd.open(ms_file)
	freq=msmd.chanfreqs(sw)								
	msmd.done()
	return freq									

def makebl(ant1,ant2):
	mybl = ant1+'&'+ant2
	return mybl


def getbllists(myfile):
	myfields = getfields(myfile)
	myallscans =[]
	for i in range(0,len(myfields)):
		myallscans.extend(getscans(myfile, myfields[i]))
	myantlist = getantlist(myfile1,int(myallscans[0]))
	allbl=[]
	for i in range(0,len(myantlist)):
		for j in range(0,len(myantlist)):
			if j>i:
				allbl.append(makebl(myantlist[i],myantlist[j]))
	mycc=[]
	mycaa=[]
	for i in range(0,len(allbl)):
		if allbl[i].count('C')==2:
			mycc.append(allbl[i])
		else:
			mycaa.append(allbl[i])
	myshortbl =[]
	myshortbl.append(str('; '.join(mycc)))
	mylongbl =[]
	mylongbl.append(str('; '.join(mycaa)))
	return myshortbl, mylongbl


def myvisstatampraw1(myfile,myfield,myspw,myant,mycorr,myscan):
	default(visstat)
	mystat = visstat(vis=myfile,axis="amp",datacolumn="data",useflags=False,spw=myspw,
		field=myfield,selectdata=True,antenna=myant,uvrange="",timerange="",
		correlation=mycorr,scan=myscan,array="",observation="",timeaverage=False,
		timebin="0s",timespan="",maxuvwdistance=0.0,disableparallel=None,ddistart=None,
		taql=None,monolithic_processing=None,intent="",reportingaxes="ddid")
	mymean1 = mystat['DATA_DESC_ID=0']['mean']
	return mymean1

def myvisstatampraw(myfile,myspw,myant,mycorr,myscan):
	default(visstat)
	mystat = visstat(vis=myfile,axis="amp",datacolumn="data",useflags=False,spw=myspw,
		selectdata=True,antenna=myant,uvrange="",timerange="",
		correlation=mycorr,scan=myscan,array="",observation="",timeaverage=False,
		timebin="0s",timespan="",maxuvwdistance=0.0,disableparallel=None,ddistart=None,
		taql=None,monolithic_processing=None,intent="",reportingaxes="ddid")
	mymean1 = mystat['DATA_DESC_ID=0']['mean']
	return mymean1

######## Reading property of the data ####

data_ms = 'JAN_19TH_GWB.ms'
data_ms_GMRT = 'JAN_19TH_GWB_using_import_GMRT.ms'


nchan = getnchan(data_ms)  ## total number of chans ##
print "The number of channels in your file:", nchan
freq = freq_info(data_ms)

## setting channel ranges for calibration and flagging ###

if nchan == 1024:
     goodchans = '0:250~300'   # used for visstat
     flagspw = '0:51~950'   ## this is the channel used to do initial cal and flagging and applycal
     gainspw = '0:101~900'
		
elif nchan == 2048:
	goodchans = '0:500~600'   # used for visstat
	flagspw = '0:101~1900'
	gainspw = '0:201~1800'
	
elif nchan == 4096:
	goodchans = '0:1000~1200'
	flagspw = '0:41~4050'
	gainspw = '0:201~3600'
	
elif nchan == 8192:
	goodchans = '0:2000~3000'
	flagspw = '0:500~7800'
	gainspw = '0:1000~7000'
	
elif nchan == 16384:
	goodchans = '0:4000~6000'
	flagspw = '0:1000~14500'
	gainspw = '0:2000~13500'
	
elif nchan == 128:
	goodchans = '0:50~70'
	flagspw = '0:5~115'
	gainspw = '0:11~115'
	gainspw2 = ''   # central good channels after split file for self-cal
elif nchan == 256:
	goodchans = '0:100~120'
	flagspw = '0:11~240'
	gainspw = '0:21~230'
	
elif nchan == 512:
	goodchans = '0:200~240'
	flagspw = '0:21~480'
	gainspw = '0:41~460'
		




myfields = getfields(data_ms) ##field names 
stdcals = ['3C48','3C147','3C286','0542+498','1331+305','0137+331']
vlacals = np.loadtxt('../../arnab_modified_full_resolution/vla-cals.list',dtype='string')
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

print "Amplitude caibrators are", myampcals
print "Phase calibrators are", mypcals
print "Target sources are", mytargets

### Taking the scans of different calibrators and target ## 

ampcalscans =[]
for i in range(0,len(myampcals)):
	ampcalscans.extend(getscans(data_ms, myampcals[i]))

pcalscans=[]
for i in range(0,len(mypcals)):
	pcalscans.extend(getscans(data_ms, mypcals[i]))

tgtscans=[]
for i in range(0,len(mytargets)):
	tgtscans.extend(getscans(data_ms,mytargets[i]))


allscanlist = ampcalscans+pcalscans+tgtscans

all_calibrator_scan_list = ampcalscans+pcalscans

flux_cal_scan_str = ','.join([str(ii) for ii in ampcalscans]) 
phase_cal_scan_str = ','.join([str(jj) for jj in pcalscans]) 
target_scan_str = ','.join([str(kk) for kk in tgtscans])
all_cal_scan_str = ','.join([str(pp) for pp in all_calibrator_scan_list]) 

print "Flux calibrator scans:", flux_cal_scan_str
print "Phase calibrator scans:", phase_cal_scan_str	
print "Target  scans:", target_scan_str

###################################
# get a list of antennas
antsused = getantlist(data_ms,int(allscanlist[0]))
print antsused

ant_id = getantid(data_ms, int(allscanlist[0]))
###################################
# find band ants
flagbadants = False
findbadants = True

if flagbadants==True:
	findbadants = True


if findbadants == True:
	myantlist = ant_id
#['C00', 'C01', 'C02', 'C03', 'C04', 'C05', 'C06', 'C08', 'C09', 'C10', 'C11', 'C12', 'C13', 'C14', 'E02', 'E03', 'E04', 'E05', 'E06', 'S01', 'S02', 'S03', 'S04', 'S06', 'W01', 'W02', 'W03', 'W04', 'W05', 'W06']
	mycmds = []
	meancutoff = 0.4    # uncalibrated mean cutoff
	mycorr1='rr'
	mycorr2='ll'
	#mygoodchans1 = mygoodchans
	mycalscans = ampcalscans+pcalscans
	print mycalscans
#	myscan1 = pcalscans
	allbadants=[]
	for j in range(0,len(mycalscans)):
		myantmeans = []
		badantlist = []
		for i in range(0,len(myantlist)):
			oneantmean1 = myvisstatampraw(data_ms,goodchans,str(myantlist[i]),mycorr1,str(mycalscans[j]))
			oneantmean2 = myvisstatampraw(data_ms,goodchans,str(myantlist[i]),mycorr2,str(mycalscans[j]))
			oneantmean = min(oneantmean1,oneantmean2)
			myantmeans.append(oneantmean)
#			print myantlist[i], oneantmean1, oneantmean2
			if oneantmean < meancutoff:
				badantlist.append(str(myantlist[i]))
				allbadants.append(str(myantlist[i]))
		print "The following antennas are bad for the given scan numbers."
		print badantlist, str(mycalscans[j])
		if badantlist!=[]:
			myflgcmd = "mode='manual' antenna='%s' scan='%s'" % (str('; '.join(badantlist)), str(mycalscans[j]))
			mycmds.append(myflgcmd)
			print myflgcmd
			onelessscan = mycalscans[j] - 1
			onemorescan = mycalscans[j] + 1
			if onelessscan in tgtscans:
				myflgcmd = "mode='manual' antenna='%s' scan='%s'" % (str('; '.join(badantlist)), str(mycalscans[j]-1))
				mycmds.append(myflgcmd)
				print myflgcmd
			if onemorescan in tgtscans:
				myflgcmd = "mode='manual' antenna='%s' scan='%s'" % (str('; '.join(badantlist)), str(mycalscans[j]+1))
				mycmds.append(myflgcmd)
				print myflgcmd
# execute the flagging commands accumulated in cmds
	print mycmds
	if flagbadants==True:
		print "Now flagging the bad antennas."
		default(flagdata)
		flagdata(vis=data_ms,mode='list', inpfile=mycmds)


######### Bad channel flagging for known persistent RFI.
flagbadfreq = False
findbadchans = True

if flagbadfreq==True:
	findbadchans = True

if findbadchans ==True:
	rfifreqall =[0.36E09,0.3796E09,0.486E09,0.49355E09,0.8808E09,0.885596E09,0.7646E09,0.769092E09] # always bad
	myfreqs =  freq_info(data_ms)
	mybadchans=[]
	for j in range(0,len(rfifreqall)-1,2):
			
		for i in range(0,len(myfreqs)):
			if (myfreqs[i] > rfifreqall[j] and myfreqs[i] < rfifreqall[j+1]):
				mybadchans.append('0:'+str(i))
	mychanflag = str(', '.join(mybadchans))
		
	if mybadchans!=[]:
			
		myflgcmd = ["mode='manual' spw='%s'" % (mychanflag)]
		if flagbadfreq==True:
			default(flagdata)
			flagdata(vis=myfile1,mode='list', inpfile=myflgcmd)
	else:
		print "No bad frequencies found in the range."


