# Run Record: phase0-ds003745-fmriprep-remaining46

- Timestamp: 20260822-222650
- Branch: main
- Commit: e26786b
- Host: CLA19787.tu.temple.edu
- User: tug87422
- Working directory: `/ZPOOL/data/projects/sharedreward-aging`
- Raw log: `/ZPOOL/data/projects/sharedreward-aging/logs/runs/20260822-222650_phase0-ds003745-fmriprep-remaining46.log`
- Command exit: 123
- Check exit: none
- Summary: COMMAND exit 123; CHECK none.

## Command

```bash
env FMRIPREP_NPROCS=12 FMRIPREP_OMP_NTHREADS=4 FMRIPREP_MEM_MB=32000 bash code/run_fmriprep_ds003745_batch.sh --manifest logs/runlists/ds003745-fmriprep-remaining.tsv --jobs 6 
```

## Log

```text
260823-03:29:33,658 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.bold_task_sharedreward_run_02_wf.bold_std_wf.fmap_recon" in "/scratch/fmriprep_25_2_wf/sub_159_wf/bold_task_sharedreward_run_02_wf/bold_std_wf/_in_tuple_MNI152NLin6Asym.resnative/fmap_recon".
260823-03:29:33,658 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.bold_task_sharedreward_run_01_wf.carpetplot_wf.parcels" in "/scratch/fmriprep_25_2_wf/sub_159_wf/bold_task_sharedreward_run_01_wf/carpetplot_wf/parcels".
260823-03:29:33,659 nipype.workflow INFO:
	 [Node] Setting-up "_anat2std_tpms1" in "/scratch/fmriprep_25_2_wf/sub_159_wf/ds_std_volumes_wf/_in_tuple_MNI152NLin6Asym.resnative/anat2std_tpms/mapflow/_anat2std_tpms1".
260823-03:29:33,660 nipype.workflow INFO:
	 [Node] Setting-up "_anat2std_tpms2" in "/scratch/fmriprep_25_2_wf/sub_159_wf/ds_std_volumes_wf/_in_tuple_MNI152NLin6Asym.resnative/anat2std_tpms/mapflow/_anat2std_tpms2".
260823-03:29:33,661 nipype.workflow INFO:
	 [Node] Executing "parcels" <nipype.interfaces.utility.wrappers.Function>
260823-03:29:33,661 nipype.workflow INFO:
	 [Node] Executing "fmap_recon" <fmriprep.interfaces.resampling.ReconstructFieldmap>
260823-03:29:33,661 nipype.workflow INFO:
	 [Node] Executing "_anat2std_tpms1" <niworkflows.interfaces.fixes.FixHeaderApplyTransforms>
260823-03:29:33,662 nipype.workflow INFO:
	 [Node] Executing "_anat2std_tpms2" <niworkflows.interfaces.fixes.FixHeaderApplyTransforms>
260823-03:29:33,677 nipype.workflow INFO:
	 [Node] Finished "parcels", elapsed time 0.01622s.
260823-03:29:34,260 nipype.workflow INFO:
	 [Node] Finished "fmap_recon", elapsed time 1.457786s.
260823-03:29:34,796 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.bold_task_sharedreward_run_02_wf.carpetplot_wf.parcels" in "/scratch/fmriprep_25_2_wf/sub_159_wf/bold_task_sharedreward_run_02_wf/carpetplot_wf/parcels".
260823-03:29:34,796 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.bold_task_sharedreward_run_01_wf.carpetplot_wf.conf_plot" in "/scratch/fmriprep_25_2_wf/sub_159_wf/bold_task_sharedreward_run_01_wf/carpetplot_wf/conf_plot".
260823-03:29:34,800 nipype.workflow INFO:
	 [Node] Executing "parcels" <nipype.interfaces.utility.wrappers.Function>
260823-03:29:34,805 nipype.workflow INFO:
	 [Node] Executing "conf_plot" <fmriprep.interfaces.confounds.FMRISummary>
260823-03:29:34,813 nipype.workflow INFO:
	 [Node] Finished "parcels", elapsed time 0.013198s.
260823-03:29:35,158 nipype.workflow INFO:
	 [Node] Finished "fmap_recon", elapsed time 1.496638s.
260823-03:29:36,347 nipype.workflow INFO:
	 [Node] Finished "conf_plot", elapsed time 1.541463s.
260823-03:29:36,798 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.bold_task_sharedreward_run_01_wf.bold_std_wf.resample" in "/scratch/fmriprep_25_2_wf/sub_159_wf/bold_task_sharedreward_run_01_wf/bold_std_wf/_in_tuple_MNI152NLin6Asym.resnative/resample".
260823-03:29:36,802 nipype.workflow INFO:
	 [Node] Executing "resample" <fmriprep.interfaces.resampling.ResampleSeries>
260823-03:29:38,882 nipype.workflow INFO:
	 [Node] Finished "_anat2std_tpms0", elapsed time 7.124479s.
260823-03:29:40,716 nipype.workflow INFO:
	 [Node] Finished "_anat2std_tpms1", elapsed time 7.053495s.
260823-03:29:40,826 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.bold_task_sharedreward_run_02_wf.carpetplot_wf.conf_plot" in "/scratch/fmriprep_25_2_wf/sub_159_wf/bold_task_sharedreward_run_02_wf/carpetplot_wf/conf_plot".
260823-03:29:40,829 nipype.workflow INFO:
	 [Node] Finished "_anat2std_tpms2", elapsed time 7.166644s.
260823-03:29:40,832 nipype.workflow INFO:
	 [Node] Executing "conf_plot" <fmriprep.interfaces.confounds.FMRISummary>
260823-03:29:42,298 nipype.workflow INFO:
	 [Node] Finished "conf_plot", elapsed time 1.464774s.
260823-03:29:42,802 nipype.workflow INFO:
	 [Node] Setting-up "_anat2std_tpms0" in "/scratch/fmriprep_25_2_wf/sub_159_wf/ds_std_volumes_wf/_in_tuple_MNI152NLin6Asym.resnative/anat2std_tpms/mapflow/_anat2std_tpms0".
260823-03:29:42,803 nipype.workflow INFO:
	 [Node] Cached "_anat2std_tpms0" - collecting precomputed outputs
260823-03:29:42,803 nipype.workflow INFO:
	 [Node] "_anat2std_tpms0" found cached.
260823-03:29:42,804 nipype.workflow INFO:
	 [Node] Setting-up "_anat2std_tpms1" in "/scratch/fmriprep_25_2_wf/sub_159_wf/ds_std_volumes_wf/_in_tuple_MNI152NLin6Asym.resnative/anat2std_tpms/mapflow/_anat2std_tpms1".
260823-03:29:42,805 nipype.workflow INFO:
	 [Node] Cached "_anat2std_tpms1" - collecting precomputed outputs
260823-03:29:42,805 nipype.workflow INFO:
	 [Node] "_anat2std_tpms1" found cached.
260823-03:29:42,805 nipype.workflow INFO:
	 [Node] Setting-up "_anat2std_tpms2" in "/scratch/fmriprep_25_2_wf/sub_159_wf/ds_std_volumes_wf/_in_tuple_MNI152NLin6Asym.resnative/anat2std_tpms/mapflow/_anat2std_tpms2".
260823-03:29:42,806 nipype.workflow INFO:
	 [Node] Cached "_anat2std_tpms2" - collecting precomputed outputs
260823-03:29:42,806 nipype.workflow INFO:
	 [Node] "_anat2std_tpms2" found cached.
260823-03:29:45,510 nipype.workflow INFO:
	 [Node] Finished "resample", elapsed time 8.707097s.
260823-03:29:46,120 nipype.workflow INFO:
	 [Node] Finished "anat2std_t1w", elapsed time 17.323807s.
260823-03:29:47,54 nipype.workflow INFO:
	 [Node] Finished "t1w_std", elapsed time 18.26407s.
260823-03:29:47,677 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.bold_task_sharedreward_run_02_wf.bold_std_wf.resample" in "/scratch/fmriprep_25_2_wf/sub_159_wf/bold_task_sharedreward_run_02_wf/bold_std_wf/_in_tuple_MNI152NLin6Asym.resnative/resample".
260823-03:29:47,678 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.bold_task_sharedreward_run_01_wf.ds_bold_std_wf.ds_bold" in "/scratch/fmriprep_25_2_wf/sub_159_wf/bold_task_sharedreward_run_01_wf/ds_bold_std_wf/_in_tuple_MNI152NLin6Asym.resnative/ds_bold".
260823-03:29:47,680 nipype.workflow INFO:
	 [Node] Executing "resample" <fmriprep.interfaces.resampling.ResampleSeries>
260823-03:29:47,687 nipype.workflow INFO:
	 [Node] Executing "ds_bold" <fmriprep.interfaces.DerivativesDataSink>
260823-03:29:52,398 nipype.workflow INFO:
	 [Node] Finished "ds_bold", elapsed time 4.710809s.
260823-03:29:56,187 nipype.workflow INFO:
	 [Node] Finished "resample", elapsed time 8.505807s.
260823-03:29:56,782 nipype.workflow INFO:
	 [Node] Finished "mask_std", elapsed time 27.990009s.
260823-03:29:57,43 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.anat_fit_wf.anat_reports_wf.norm_msk" in "/scratch/fmriprep_25_2_wf/sub_159_wf/anat_fit_wf/anat_reports_wf/_in_tuple_MNI152NLin6Asym.resnative/norm_msk".
260823-03:29:57,43 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.bold_task_sharedreward_run_02_wf.ds_bold_std_wf.ds_bold" in "/scratch/fmriprep_25_2_wf/sub_159_wf/bold_task_sharedreward_run_02_wf/ds_bold_std_wf/_in_tuple_MNI152NLin6Asym.resnative/ds_bold".
260823-03:29:57,45 nipype.workflow INFO:
	 [Node] Executing "norm_msk" <nipype.interfaces.utility.wrappers.Function>
260823-03:29:57,47 nipype.workflow INFO:
	 [Node] Executing "ds_bold" <fmriprep.interfaces.DerivativesDataSink>
260823-03:29:57,316 nipype.workflow INFO:
	 [Node] Finished "anat2std_mask", elapsed time 28.525395s.
260823-03:29:57,632 nipype.workflow INFO:
	 [Node] Finished "norm_msk", elapsed time 0.586178s.
260823-03:29:59,30 nipype.interface WARNING:
	 Changing /base/project/derivatives/fmriprep/sub-159/anat/sub-159_space-MNI152NLin6Asym_desc-brain_mask.nii.gz dtype from float64 to float64
260823-03:29:59,502 nipype.workflow INFO:
	 [Node] Setting-up "fmriprep_25_2_wf.sub_159_wf.anat_fit_wf.anat_reports_wf.norm_rpt" in "/scratch/fmriprep_25_2_wf/sub_159_wf/anat_fit_wf/anat_reports_wf/_in_tuple_MNI152NLin6Asym.resnative/norm_rpt".
260823-03:29:59,505 nipype.workflow INFO:
	 [Node] Executing "norm_rpt" <niworkflows.interfaces.reportlets.registration.SimpleBeforeAfterRPT>
260823-03:30:00,145 nipype.workflow INFO:
	 [Node] Finished "anat2std_dseg", elapsed time 31.360555s.
260823-03:30:01,61 nipype.interface WARNING:
	 Changing /base/project/derivatives/fmriprep/sub-159/anat/sub-159_space-MNI152NLin6Asym_dseg.nii.gz dtype from float64 to float64
260823-03:30:01,413 nipype.workflow INFO:
	 [Node] Finished "ds_bold", elapsed time 4.365943s.
260823-03:30:05,573 nipype.workflow INFO:
	 [Node] Finished "norm_rpt", elapsed time 6.067585s.
260823-03:30:08,975 nipype.workflow IMPORTANT:
	 fMRIPrep finished successfully!
260823-03:30:08,979 nipype.workflow IMPORTANT:
	 Works derived from this fMRIPrep execution should include the boilerplate text found in <OUTPUT_PATH>/logs/CITATION.md.

COMMAND EXIT: 123
```
