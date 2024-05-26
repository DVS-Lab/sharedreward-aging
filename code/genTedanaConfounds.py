#!/usr/bin/env python


import matplotlib.pyplot as plt
import os
import pandas as pd
from natsort import natsorted
import re
import numpy as np


fmriprep_dir='../derivatives/fmriprep/'
tedana_dir='../derivatives/tedana/'



metric_files = natsorted([os.path.join(root,f) for root,dirs,files in os.walk(
    '../derivatives/tedana/') for f in files if f.endswith("tedana_metrics.tsv")])
subs=set([re.search("tedana/(.*)/sub-",file).group(1) for file in metric_files])


for file in metric_files:
	
    #Read in the directory, sub-num, and run-num
    base=re.search("(.*)tedana_metrics",file).group(1)

    run=re.search("run-(.*)_desc-tedana",file).group(1)
    sub=re.search("tedana/(.*)/sub-",file).group(1)

    
    #import the data as dataframes
    fmriprep_fname="../derivatives/fmriprep/%s/func/%s_task-sharedreward_run-%s_part-mag_desc-confounds_timeseries.tsv"%(sub,sub,run)

    if os.path.exists(fmriprep_fname):
        print("Making Confounds: %s %s"%(sub,run))
        fmriprep_confounds=pd.read_csv(fmriprep_fname,sep='\t')
        ICA_mixing=pd.read_csv('%sICA_mixing.tsv'%(base),sep='\t')
        metrics=pd.read_csv('%stedana_metrics.tsv'%(base),sep='\t')
        bad_components=ICA_mixing[metrics[metrics['classification']=='rejected']['Component']]


        aCompCor =['a_comp_cor_00','a_comp_cor_01','a_comp_cor_02','a_comp_cor_03','a_comp_cor_04','a_comp_cor_05']
        cosine = [col for col in fmriprep_confounds if col.startswith('cosine')]
        NSS = [col for col in fmriprep_confounds if col.startswith('non_steady_state')]
        motion = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z']
        fd = ['framewise_displacement']
        filter_col=np.concatenate([aCompCor,cosine,NSS,motion,fd])
        fmriprep_confounds=fmriprep_confounds[filter_col]

        #Combine horizontally
        tedana_confounds=pd.concat([bad_components], axis=1)
        confounds_df=pd.concat([fmriprep_confounds, tedana_confounds], axis=1)
        #Output in fsl-friendly format
        outfname='../derivatives/fsl/confounds_tedana/%s/%s_task-sharedreward_run-%s_desc-TedanaPlusConfounds.tsv'%(sub,sub,run)
        os.makedirs('../derivatives/fsl/confounds_tedana/%s'%(sub),exist_ok=True)
        confounds_df.to_csv(outfname,index=False,header=False,sep='\t')
    else:
        print("fmriprep failed for %s %s"%(sub,run))
