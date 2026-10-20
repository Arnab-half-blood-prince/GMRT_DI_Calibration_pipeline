import stimela
from stimela.pathformatter import pathformatter as spf
INPUT="input"
MSDIR="msdir"
OUTPUT="output"
ms1="Target_24th_June_2018.ms"
ms2="Target_30th_June_2018.ms"

ms_files = [ms1,ms2]

diconame='image_DI.DicoModel'
regions = ["dE_1.reg"] # the regions to be peeled, can be more than one region

subtract_part = "+-".join(
    ["{{}}{}@{{}}{}".format(diconame, reg) for reg in regions]
)
direction_part = ":".join(
    ["{{}}{}@{{}}{}".format(diconame, reg) for reg in regions]
)
model_list_string = "MODEL_DATA+-" + subtract_part + ":" + direction_part
print(f"{model_list_string}")

recipe = stimela.Recipe("peeling all source",
                         ms_dir=MSDIR,
                         JOB_TYPE="docker")





#diconame='image_DI.DicoModel'
#tagregs='dE_1.reg'

#for ii in range(1,2):
for ii in range(len(ms_files)):

    recipe.add("cab/cubical_ddf", "dE calibrate region 1 of {} ms".format(ii), {
                'data-ms': ms_files[ii],
                'data-column': 'DATA',
                'dist-ncpu': 40,
                'dist-nthread': 0,
                'dist-max-chunks': 8, ## the data sets will be divided in these many chunks
                'data-time-chunk': 50,  ## 50 time solts (int time), should be equal or greater than time solution option
                'data-freq-chunk': 128,  ## ## 64 freq solts (channels), should be equal or greater than freq solution option
                #'model-list': spf("MODEL_DATA+-{{}}{}@{{}}{}:{{}}{}@{{}}{}".format(diconame, tagregs, diconame, tagregs),
                #                  "output", "output", "output", "output"),
                'model-list': spf(model_list_string,*["output"] * (4 * len(regions))),
                'weight-column': "WEIGHT",
                'flags-apply': "FLAG",
                'flags-auto-init': "legacy",
                'madmax-enable': False,
                'madmax-threshold': [0,0,10],
                'madmax-global-threshold': [0,0],
                'sol-jones': 'g,dd',
                'sol-min-bl': 0.,
                'sol-max-bl': 0,
                'sol-stall-quorum': 0.95,
                'sol-term-iters': [50,90,50,90],
                'out-name': 'peeling_28.cc-out',

                'out-mode': 'sr',
                'out-column': 'CORRECTED_DATA',  ## sr means solve and peel and give residual in the corrected column
                #'out-model-column': "MODEL_OUT",
                'log-verbose': "solver=2",
                'dd-time-int': 50,  ## 50*int_time
                'dd-freq-int': 128, ## 64*chans
                "dd-prop-flags": 'always',
                'dd-type': 'complex-2x2',
                'g-type': 'complex-2x2',
                'g-freq-int': 128,  ## 64*chans
                'g-time-int': 30,  ## 30*int_time
                'g-max-iter': 100,
                'g-update-type': "phase-diag",
                'dd-max-iter': 200,
                'dd-clip-high': 0,
                'dd-clip-low': 0,
                #'dd-fix-dirs': "0",
                'out-subtract-dirs': ':',
                'dd-dd-term': True,
                'dd-max-prior-error': 0.35,
                'dd-max-post-error': 0.35,
                'g-clip-high': 0,
                'g-clip-low': 0,
                'g-max-prior-error': 0.35,
                'g-max-post-error': 0.35,
                'degridding-NDegridBand': 4,
                'degridding-MaxFacetSize': 0.15
        }, input=INPUT, output=OUTPUT, label="de_calibrate reg-1  of {} ms".format(ii), shared_memory="250g")
        
    recipe.add("cab/casa_flagdata", "flagging residual phase cal loop {} ms".format(ii),{
     "msname": ms_files[ii],
     "mode":'tfcrop',
     "timecutoff":4.0,
     "freqcutoff":5.0,
     "timefit": "line",
     "freqfit": "poly",
     "flagdimension": "freqtime",
     "usewindowstats":'both',
     "halfwin":2,
     "datacolumn": "RESIDUAL",
     "extendflags":False, 
     "action": "apply",
        }, input=INPUT, output=OUTPUT, label="flag after DD cal loop {} ms".format(ii))    

    recipe.run()

recipe_im = stimela.Recipe("Image after all source peel",ms_dir=MSDIR,JOB_TYPE="docker")

recipe_im.add("cab/wsclean", "Image after all source peeled", {
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
     "auto-mask": 6,
     "auto-threshold":3,
     "threshold":0.1e-3,
     "weight":'briggs -1',
     "niter": 500000,
     "name": "Abs_2018_after_all_src_peeled",
     
}, input=INPUT, output=OUTPUT, label="peeled masked image")

recipe_im.run()