import stimela

INPUT="input"
MSDIR="msdir"
OUTPUT="output"


ms1="Target_24th_June_2018.ms"
#ms2="Target_30th_June_2018.ms"
ref_ant_1 = "25,26,15,16"
#ref_ant_2 = "3,9,5,2"

ms_files = [ms1]
ref_ant = [ref_ant_1]

### Self cal parameters ## 

uvrange = '>1.5klambda'
soltime = ['8min','6min','4min','2min']  ## solution time interval
ncycles = 4                              ## the number of phase cal cycles
thresh = [1e-3,0.5e-3,0.2e-3,0.1e-3]     ## clean threshold
sigma = [6,5,5,5] ## The sigma clipping for generating CLEAN mask, I assume you already have a mask created for first cycle of name halo_mask_0.fits, check the last cleanmask task and provide yours.

iteration = [100000,130000,150000,200000] # CLEAN threshold



recipe_first = stimela.Recipe("First masked  image",ms_dir=MSDIR,JOB_TYPE="docker")
 
recipe_first.add("cab/wsclean", "mask", {
     "msname": ms_files,
     "datacolumn": "DATA",
     "multiscale":True,
     "join-channels": True,
     "channels-out": 2,
     "fit-spectral-pol":2,
     "size": [8192,8192],
     "scale": "2.0asec",
     "mgain": 0.8,
     "weighting-rank-filter":3,
     "weighting-rank-filter-size": 32, 
     "fitsmask":"mask_2022_combined.fits:output",
     "threshold":1e-3,
     "weight":'briggs -1',
     "niter": 500000,
     "name": "Abs_first_masked_2018_combined",
     
}, input=INPUT, output=OUTPUT, label="first masked")
 
recipe_first.run()

# Now do the selfcal - phase only 

recipe = stimela.Recipe("Phase selfcal",ms_dir=MSDIR,JOB_TYPE="docker")
                        

for jj in range(ncycles):

    for ii in range(len(ms_files)):

        recipe.add("cab/casa_gaincal", "calibrating {} ms".format(ii),{

     "msname": ms_files[ii],
     "caltable":'gain_'+str(ii)+'th_ms.'+str(jj),
     "field":'0',
     "refant":ref_ant[ii],
     "gaintype":'G',
     "refantmode":'flex',
     "solint":soltime[jj],
     "minsnr":3,
     "minblperant": 6,
     "uvrange":uvrange,
     "calmode":'p' 
 }, input=INPUT, output=OUTPUT, label="cal {} ms".format(ii))

        recipe.add("cab/msutils", "plot_gains {} ms".format(ii), {
   
     "command": "plot_gains",
     "ctable": 'gain_'+str(ii)+'th_ms.'+str(jj)+':output',
     "tabtype": "gain",
     "plot_file": 'gains_'+str(ii)+'th_ms_'+str(jj)+'.png',
     "subplot_scale": 4,
     "plot_dpi": 180,
 }, input=INPUT, output=OUTPUT, label="plot gains {} ms".format(ii))




        recipe.add("cab/casa_applycal", "applying {} ms".format(ii),{
     "msname": ms_files[ii],
     "gaintable":['gain_'+str(ii)+'th_ms.'+str(jj)+':output'],
     "applymode":'calflagstrict',
     "calwt":False,
 }, input=INPUT, output=OUTPUT, label="apply to {} ms".format(ii))


        recipe.add("cab/casa_flagdata", "flagging residual phase cal loop {} ms".format(ii),{
     "msname": ms_files[ii],
     "mode":'tfcrop',
     "timecutoff":6.0,
     "freqcutoff":6.0,
     "timefit": "line",
     "freqfit": "poly",
     "flagdimension": "freqtime",
     "usewindowstats":'both',
     "halfwin":2,
     "datacolumn": "RESIDUAL",
     "extendflags":False, 
     "action": "apply",
 }, input=INPUT, output=OUTPUT, label="flag phase cal loop {} ms".format(ii))
    #recipe.run("flag {} ms".format(ii))
    

        recipe.add('cab/msutils', "Copy corr column to data of {} ms".format(ii), {
          "command" : 'copycol',
          "msname"  : ms_files[ii],
          "fromcol" : 'CORRECTED_DATA',
          "tocol"   : 'DATA',
}, input=INPUT, output=OUTPUT, label="copy {} ms".format(ii))



    recipe.add("cab/wsclean", "Image after selfcal_{}".format(jj), {
     "msname": ms_files,
     "datacolumn": "CORRECTED_DATA",
     "multiscale":True,
     "join-channels": True,
     "channels-out": 2,
     "fit-spectral-pol":2,
     "size": [8192, 8192],
     "scale": "2.0asec",
     "mgain": 0.8,
     "weighting-rank-filter":3,
     "weighting-rank-filter-size": 32, 
     "auto-mask": 7,
     "auto-threshold":3,
     "threshold":thresh[jj],
     "weight":'briggs -1',
     "niter": iteration[jj],
     "name": "Abs_2018_masked_"+str(jj),
     
}, input=INPUT, output=OUTPUT, label="mask image")
 
 
 
    recipe.run()