# CASA 5.6.3 compatible pipeline:
# uvsub -> split -> uvcontsub -> mstransform(BARY) -> dirty tclean cube
#
# Run inside CASA 5:
#   execfile('run_uvsub_uvcontsub_bary_dirtycube_casa5.py')
#
# IMPORTANT:
# - This script assumes MODEL_DATA already exists in each input MS.
# - uvsub(reverse=False) subtracts MODEL_DATA from DATA.
# - reverse=True would add the model back, so do not use reverse=True here.

import os
import shutil

# -------------------------------------------------------------------
# User settings
# -------------------------------------------------------------------

ms_files = [
    "Target_common_band_DD_24th_June_2018_no_uvsub.ms",
    "Target_common_band_DD_30th_June_2018_no_uvsub.ms",
    "Target_common_band_DD_17th_July_2022_no_uvsub.ms",
    "Target_common_band_DD_27th_Aug_2022_no_uvsub.ms",
    "Target_common_band_DD_28th_Nov_2022_no_uvsub.ms",
]

# If True, remove existing intermediate outputs before recreating them.
OVERWRITE = False

# uvcontsub settings
UVCONTSUB_FITORDER = 2
UVCONTSUB_FITSPW = "0:4587~5079"          # full frequency range, except the QSO location
UVCONTSUB_EXCLUDECHANS = True # no excluded channels


# -------------------------------------------------------------------
# Helper functions
# -------------------------------------------------------------------

def remove_ms(path):
    if os.path.exists(path):
        if not OVERWRITE:
            raise RuntimeError(
                "Output exists: {0}\n"
                "Set OVERWRITE=True if you want to delete and recreate it.".format(path)
            )
        print("Removing existing output: {0}".format(path))
        shutil.rmtree(path)


def uvsub_output_name(ms):
    """
    Convert:
      Target_common_band_DD_24th_June_2018_no_uvsub.ms
    to:
      Target_common_band_DD_24th_June_2018.uvsub.ms
    """
    if ms.endswith("_no_uvsub.ms"):
        return ms.replace("_no_uvsub.ms", ".uvsub.ms")
    if ms.endswith(".ms"):
        return ms.replace(".ms", ".uvsub.ms")
    return ms + ".uvsub.ms"


def contsub_output_name(uvsub_ms):
    return uvsub_ms + ".contsub"


def barry_output_name(contsub_ms):
    return contsub_ms + ".barry"


def check_input_ms(ms):
    if not os.path.exists(ms):
        raise IOError("Input MS not found: {0}".format(ms))


def run_uvsub_and_split(input_ms, output_uvsub_ms):
    """
    uvsub modifies the input MS by writing subtracted data to CORRECTED_DATA.
    split then writes CORRECTED_DATA to a clean .uvsub.ms, with that data in DATA.
    """
    print("\n" + "=" * 80)
    print("UVSUB: {0}".format(input_ms))
    print("=" * 80)

    uvsub(
        vis=input_ms,
        reverse=False,
    )

    remove_ms(output_uvsub_ms)

    print("SPLIT corrected data to: {0}".format(output_uvsub_ms))
    split(
        vis=input_ms,
        outputvis=output_uvsub_ms,
        datacolumn="corrected",
        keepflags=True,
    )


def run_uvcontsub(input_uvsub_ms):
    """
    CASA uvcontsub creates:
      input_uvsub_ms + ".contsub"
    when want_cont=False.
    """
    output_contsub_ms = contsub_output_name(input_uvsub_ms)
    remove_ms(output_contsub_ms)

    print("\n" + "=" * 80)
    print("UVCONTSUB: {0}".format(input_uvsub_ms))
    print("Excluding fit channels: {0}".format(UVCONTSUB_FITSPW))
    print("=" * 80)

    uvcontsub(
        vis=input_uvsub_ms,
        field="",
        fitspw=UVCONTSUB_FITSPW,
        excludechans=UVCONTSUB_EXCLUDECHANS,
        combine="",
        solint="int",
        fitorder=UVCONTSUB_FITORDER,
        spw="",
        want_cont=False,
    )

    if not os.path.exists(output_contsub_ms):
        raise RuntimeError(
            "Expected uvcontsub output not found: {0}\n"
            "Check your CASA uvcontsub version/output naming.".format(output_contsub_ms)
        )

    return output_contsub_ms


def make_barry_ms(input_contsub_ms):
    """
    Create .barry MS using your CASA mstransform setup.
    """
    output_barry_ms = barry_output_name(input_contsub_ms)
    remove_ms(output_barry_ms)

    print("\n" + "=" * 80)
    print("MSTRANSFORM to BARY frame: {0}".format(input_contsub_ms))
    print("Output: {0}".format(output_barry_ms))
    print("=" * 80)

    mstransform(
        vis=input_contsub_ms,
        outputvis=output_barry_ms,
        createmms=False,
        separationaxis="auto",
        numsubms="auto",
        tileshape=[0],
        field="",
        spw="",
        scan="",
        antenna="",
        correlation="",
        timerange="",
        intent="",
        array="",
        uvrange="",
        observation="",
        feed="",
        datacolumn="data",
        realmodelcol=False,
        keepflags=True,
        usewtspectrum=False,
        combinespws=False,
        chanaverage=False,
        chanbin=1,
        hanning=False,
        regridms=True,
        mode="channel",
        nchan=-1,
        start=0,
        width=1,
        nspw=1,
        interpolation="linear",
        phasecenter="",
        restfreq="1.4204057517667e+9Hz",
        outframe="BARY",
        veltype="radio",
        preaverage=False,
        timeaverage=False,
        timebin="0s",
        timespan="",
        maxuvwdistance=0.0,
        docallib=False,
        callib="",
        douvcontsub=False,
        fitspw="",
        fitorder=0,
        want_cont=False,
        denoising_lib=True,
        nthreads=1,
        niter=1,
        disableparallel=False,
        ddistart=-1,
        taql="",
        monolithic_processing=None,
        reindex=True,
    )

    if not os.path.exists(output_barry_ms):
        raise RuntimeError("Expected mstransform output not found: {0}".format(output_barry_ms))

    return output_barry_ms


# -------------------------------------------------------------------
# Main processing
# -------------------------------------------------------------------

uvsub_ms_files = []
contsub_ms_files = []
barry_ms_files = []

for ms in ms_files:
    check_input_ms(ms)

    uvsub_ms = uvsub_output_name(ms)
    run_uvsub_and_split(ms, uvsub_ms)
    uvsub_ms_files.append(uvsub_ms)

    contsub_ms = run_uvcontsub(uvsub_ms)
    contsub_ms_files.append(contsub_ms)

    barry_ms = make_barry_ms(contsub_ms)
    barry_ms_files.append(barry_ms)


# -------------------------------------------------------------------
# Dirty image cube with tclean
# -------------------------------------------------------------------

print("\n" + "=" * 80)
print("Final MS list for tclean:")
for v in barry_ms_files:
    print("  {0}".format(v))
print("=" * 80)

tclean(
    vis=barry_ms_files,
    selectdata=True,
    field="",
    spw="",
    timerange="",
    uvrange="",
    antenna="",
    scan="",
    observation="",
    intent="",
    datacolumn="data",
    imagename="Abs_common_band_all_nights_robust0_dirty.im",
    imsize=[512, 512],
    cell=["2.0arcsec"],
    phasecenter="",
    stokes="I",
    projection="SIN",
    startmodel="",
    specmode="cubedata",
    reffreq="",
    nchan=-1,
    start="0",
    width=2,
    outframe="BARY",
    veltype="radio",
    restfreq=["1.4204057517667e+9Hz"],
    interpolation="linear",
    perchanweightdensity=False,
    gridder="widefield",
    facets=1,
    psfphasecenter="",
    chanchunks=32,
    wprojplanes=-1,
    vptable="",
    mosweight=True,
    aterm=True,
    psterm=False,
    wbawp=True,
    conjbeams=False,
    cfcache="",
    usepointing=False,
    computepastep=360.0,
    rotatepastep=360.0,
    pointingoffsetsigdev=0.0,
    pblimit=0.2,
    normtype="flatnoise",
    deconvolver="clarkstokes",
    scales=[],
    nterms=2,
    smallscalebias=0.0,
    restoration=True,
    restoringbeam="",
    pbcor=False,
    outlierfile="",
    weighting="natural",
    noise="1.0Jy",
    npixels=0,
    uvtaper=[""],
    niter=0,
    gain=0.1,
    threshold=0.0,
    nsigma=0.0,
    cycleniter=-1,
    cyclefactor=1.0,
    minpsffraction=0.05,
    maxpsffraction=0.8,
    interactive=False,
    usemask="user",
    mask="",
    pbmask=0.0,
    sidelobethreshold=3.0,
    noisethreshold=5.0,
    lownoisethreshold=1.5,
    negativethreshold=0.0,
    smoothfactor=1.0,
    minbeamfrac=0.3,
    cutthreshold=0.01,
    growiterations=75,
    dogrowprune=True,
    minpercentchange=-1.0,
    verbose=False,
    fastnoise=True,
    restart=True,
    savemodel="none",
    calcres=True,
    calcpsf=True,
    parallel=False,
)

print("\nDONE: uvsub -> split -> uvcontsub -> mstransform(BARY) -> robust-0 dirty cube")
