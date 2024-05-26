#!/usr/bin/env python


import matplotlib.pyplot as plt
import os
import pandas as pd
from natsort import natsorted
import re
import numpy as np


fmriprep_dir='../derivatives/fmriprep-syn/'
tedana_dir='../derivatives/tedana/'

bold_imgs=[os.path.join(root,f) for root,dirs,files in os.walk(tedana_dir) for f in files if f.endswith('desc-optcom_bold.nii.gz')]


metric_files = natsorted([os.path.join(root,f) for root,dirs,files in os.walk(
    '../derivatives/tedana/') for f in files if f.endswith("PCA_metrics.tsv")])
subs=set([re.search("tedana/(.*)/sub-",file).group(1) for file in metric_files])

#for sub in subs:
#    print(sub,"has %s acqs of denoised tedana"%(sum(sub in s for s in metric_files)))

for file in metric_files:
	
    #Read in the directory, sub-number, and acquisition
    base=re.search("(.*)PCA_metrics",file).group(1)
    #sub=re.search("tedana/(.*)/sub-",file).group(1)
    #acq=re.search("acq-(.*)_desc",file).group(1)


    acq=re.search("acq-(.*)/sub-",file).group(1)
    sub=re.search("acq-" + acq + "/(.*)_task-",file).group(1)
    
    #import the data as dataframes
    fmriprep_fname="../derivatives/fmriprep-syn/%s/func/%s_task-sharedreward_acq-%s_desc-confounds_timeseries.tsv"%(sub,sub,acq)
    #print(fmriprep_fname)
    
    if os.path.exists(fmriprep_fname):
        print("Making Confounds: %s %s"%(sub,acq))
        fmriprep_confounds=pd.read_csv(fmriprep_fname,sep='\t')
        PCA_mixing=pd.read_csv('%sPCA_mixing.tsv'%(base),sep='\t')
        PCA_metrics=pd.read_csv('%sPCA_metrics.tsv'%(base),sep='\t')
        ICA_mixing=pd.read_csv('%sICA_mixing.tsv'%(base),sep='\t')
        ICA_metrics=pd.read_csv('%stedana_metrics.tsv'%(base),sep='\t')
        # Select columns from each data frame for final counfounds file
        ICA_mixing=ICA_mixing[ICA_metrics[ICA_metrics['classification']=='rejected']['Component']]
        PCA_mixing=PCA_mixing[PCA_metrics[PCA_metrics['classification']=='rejected']['Component']]

        aCompCor =['a_comp_cor_00','a_comp_cor_01','a_comp_cor_02','a_comp_cor_03','a_comp_cor_04','a_comp_cor_05']
        cosine = [col for col in fmriprep_confounds if col.startswith('cosine')]
        NSS = [col for col in fmriprep_confounds if col.startswith('non_steady_state')]
        motion = ['trans_x','trans_y','trans_z','rot_x','rot_y','rot_z']
        fd = ['framewise_displacement']
        filter_col=np.concatenate([aCompCor,cosine,NSS,motion,fd])
        fmriprep_confounds=fmriprep_confounds[filter_col]

        #Combine horizontally
        Comp_confounds=pd.concat([ICA_mixing, PCA_mixing], axis=1)
        confounds_df=pd.concat([fmriprep_confounds, Comp_confounds], axis=1)
        #Output in fsl-friendly format
        outfname='../derivatives/fsl/confounds_tedana/%s/%s_task-sharedreward_acq-%s_desc-TedanaPlusConfounds.tsv'%(sub,sub,acq)
        os.makedirs('../derivatives/fsl/confounds_tedana/%s'%(sub),exist_ok=True)
        confounds_df.to_csv(outfname,index=False,header=False,sep='\t')
    else:
        print("fmriprep failed for %s %s"%(sub,acq))
