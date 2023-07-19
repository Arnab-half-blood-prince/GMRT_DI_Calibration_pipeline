# GMRT_DI_Calibration_pipeline
Direction-Independent Calibration Pipeline

A calibration, imaging pipeline for uGMRT data The pipeline folder contains a direction independent calibration pipeline tool. This is mainly designed for direction-independent calibration of uGMRT data set. I have tested this to Band 3 (250 - 500 MHz), Band 4 (550-850 MHz) and Band 5 (1050-1450 MHz) uGMRT data.

The relevant images for different data sets are also uploaded in the test folder. If everything works well you should expect a calibration output like these as give in the weblog under the test folder.

**If you use it and find any problem kindly let me know. Any suggestions regarding improvements of the pipeline is welcome.**

The direction-dependent calibration for uGMRT wide-band data is an ongoing work and not finished yet.

Contact: arnab.phy.personal@gmail.com

# How to Run

Keep this repo on your /home/(usr_name)

Go to the directory where your dataset is located, then open CASA

 ```
 execfile('/home/usr_name/GMRT_DI_Calibration_pipeline/DI_pipeline/uGMRT_DI_calibration_pipeline/GMRT_pipeline_work.py')

```

For futher information please see **how_to_run** file in dir  **uGMRT_DI_calibration_pipeline**

# With great power comes great responsibility

For GMRT data sets

```
If you want to provide direct Visibility, make sure it is created using importuvfits task
```

# Fast

If ones wants to run this pipeline a bit faster then

set the condition **Pipeline_Fast = True** in **GMRT_pipeline_work.py**

It basily skip some steps like: _flagdata(vis="SDM.ms",mode="summary", action="calculate")_

# Pipeline stops in between 

If your pipeline stops in between and you want to skip the part which is completed. 

After it stops, open an output file "**Pipeline_working.txt**" where one can know which file tasks are completed. While running again, comment certain task in filename: **GMRT_pipeline_work.py**, but REMEMBER REMEMBER...

### Don't comment these lines in **GMRT_pipeline_work.py**

```
execfile(pipepath+'GMRT_pipe_startup.py')
execfile(pipepath+'GMRT_pipe_import.py')
execfile(pipepath+'GMRT_pipe_msinfo.py')
execfile(pipepath+'GMRT_pipe_calprep.py')
execfile(pipepath+'GMRT_pipe_priorcals.py')
execfile(pipepath+'GMRT_pipe_testBPdcals.py')

```

In Future I will try to make it better so one can provide the **Pipeline_working.txt** as a input while running the pipeline again.

Contact: mangla.sarvesh@gmail.com

# Developer 
Arnab Chakraborty (arnab.phy.personal@gmail.com) -- post-doc at McGill University.

Sarvesh Mangala (mangla.sarvesh@gmail.com) -- PhD at IIT Indore.
