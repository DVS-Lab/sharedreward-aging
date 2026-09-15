# Run Record: retained-contrasts-local-validation

- Timestamp: 20260915-090716
- Branch: main
- Commit: 4210fd1
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20260915-090716_retained-contrasts-local-validation.log`
- Command exit: 0
- Check exit: 0
- Summary: COMMAND exit 0; CHECK 0.

## Command

```bash
bash code/validate_workflow.sh 
```

## Check

```bash
python3 code/verify_neutral_feat_design.py --output logs/records/20260915-retained-contrast-feat-design.json 
```

## Log

```text
RUN START: 20260915-090716
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main 4210fd1
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: bash code/validate_workflow.sh 

PASS: bash syntax
PASS: Python syntax
test_source_misses_task_invalid_ratings_and_review_are_distinct (test_analysis_cohort.CohortTest.test_source_misses_task_invalid_ratings_and_review_are_distinct) ... ok
test_batch_and_audit_preserve_tsnr_motion_coverage_contract (test_analysis_qc.AnalysisQc.test_batch_and_audit_preserve_tsnr_motion_coverage_contract) ... ok
test_common_mask_uses_reference_grid_and_nearest_neighbor (test_analysis_qc.AnalysisQc.test_common_mask_uses_reference_grid_and_nearest_neighbor) ... ok
test_coverage_eligible_mask_subtracts_resampled_exemption (test_analysis_qc.AnalysisQc.test_coverage_eligible_mask_subtracts_resampled_exemption) ... ok
test_rf1_motion_qc_uses_named_fmriprep_table_not_feat_matrix (test_analysis_qc.AnalysisQc.test_rf1_motion_qc_uses_named_fmriprep_table_not_feat_matrix) ... ok
test_rf1_is_pinned_to_complete_sharedreward_session_01_inventory (test_characterization_inventory.CharacterizationInventoryTest.test_rf1_is_pinned_to_complete_sharedreward_session_01_inventory) ... ok
test_low_coverage_run_creates_mosaic_and_summary (test_coverage_mosaics.CoverageMosaics.test_low_coverage_run_creates_mosaic_and_summary) ... ok
test_builds_deterministic_runlist_with_exclusions (test_ds003745_runlist.Ds003745Runlist.test_builds_deterministic_runlist_with_exclusions) ... ok
test_strictly_more_than_25pct_excludes_run_not_subject_with_usable_run (test_event_qc.EventQc.test_strictly_more_than_25pct_excludes_run_not_subject_with_usable_run) ... ok
test_reports_complete_and_incomplete_participants (test_fmriprep_audit.FmriprepAudit.test_reports_complete_and_incomplete_participants) ... ok
test_missing_base_column_fails (test_fsl_confounds.FSLConfoundsTest.test_missing_base_column_fails) ... ok
test_rf1_base_policy_and_zero_fill (test_fsl_confounds.FSLConfoundsTest.test_rf1_base_policy_and_zero_fill) ... ok
test_contract_is_full_trial_only (test_fulltrial_candidate.Candidate.test_contract_is_full_trial_only) ... ok
test_ds003745_preserves_published_trial_timing_and_omits_blocks (test_harmonized_events.Events.test_ds003745_preserves_published_trial_timing_and_omits_blocks) ... Wrote 2 ds003745 full-trial rows: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpyck3zfds/out.tsv
ok
test_rf1_derives_decision_to_outcome_offset_and_miss (test_harmonized_events.Events.test_rf1_derives_decision_to_outcome_offset_and_miss) ... Wrote 2 rf1 full-trial rows: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpootfc4xc/out.tsv
ok
test_rf1_partner_mismatch_fails (test_harmonized_events.Events.test_rf1_partner_mismatch_fails) ... ok
test_missing_switch_and_changed_weights_fail (test_l1_contrast_audit.ContrastAuditTest.test_missing_switch_and_changed_weights_fail) ... ok
test_nonestimable_primary_fails (test_l1_contrast_audit.ContrastAuditTest.test_nonestimable_primary_fails) ... ok
test_retained_ids_and_empty_neutral_reporting (test_l1_contrast_audit.ContrastAuditTest.test_retained_ids_and_empty_neutral_reporting) ... ok
test_empty_inferential_condition_still_fails (test_l1_evs.L1EVTest.test_empty_inferential_condition_still_fails) ... ok
test_empty_neutral_is_written_as_an_optional_empty_ev (test_l1_evs.L1EVTest.test_empty_neutral_is_written_as_an_optional_empty_ev) ... ok
test_render_only_activation_and_ppi_resolve_the_pooled_contract (test_l1_runner.L1RunnerTest.test_render_only_activation_and_ppi_resolve_the_pooled_contract) ... ok
test_manifest_separates_fixed_effects_from_one_run_passthrough (test_l2_runner.L2RunnerTest.test_manifest_separates_fixed_effects_from_one_run_passthrough) ... ok
test_runtime_transform_preserves_fixed_effects_and_expands_copes (test_l2_runner.L2RunnerTest.test_runtime_transform_preserves_fixed_effects_and_expands_copes) ... ok
test_l1_failure_still_waits_for_ppi (test_parallel_analysis_types.ParallelTypesTest.test_l1_failure_still_waits_for_ppi) ... ok
test_l1_types_overlap (test_parallel_analysis_types.ParallelTypesTest.test_l1_types_overlap) ... ok
test_l2_failure_still_waits_for_ppi (test_parallel_analysis_types.ParallelTypesTest.test_l2_failure_still_waits_for_ppi) ... ok
test_l2_types_overlap (test_parallel_analysis_types.ParallelTypesTest.test_l2_types_overlap) ... ok
test_download_is_limited_to_sharedreward_bold_runs (test_phase0_acquisition_contract.Phase0AcquisitionContract.test_download_is_limited_to_sharedreward_bold_runs) ... ok
test_fmriprep_is_limited_to_sharedreward_task (test_phase0_acquisition_contract.Phase0AcquisitionContract.test_fmriprep_is_limited_to_sharedreward_task) ... ok
test_source_data_are_not_tracked_by_parent_repository (test_phase0_acquisition_contract.Phase0AcquisitionContract.test_source_data_are_not_tracked_by_parent_repository) ... ok
test_activation_is_narrow_fulltrial_contract (test_pooled_fsf.PooledFSFTest.test_activation_is_narrow_fulltrial_contract) ... ok
test_active_templates_disable_per_ev_temporal_filtering (test_pooled_fsf.PooledFSFTest.test_active_templates_disable_per_ev_temporal_filtering) ... ok
test_ppi_uses_10_psych_phys_and_10_interactions (test_pooled_fsf.PooledFSFTest.test_ppi_uses_10_psych_phys_and_10_interactions) ... ok
test_equality_is_allowed_but_loss_greater_than_win_is_excluded (test_ratings_qc.RatingsQc.test_equality_is_allowed_but_loss_greater_than_win_is_excluded) ... ok
test_manifest_preserves_source_path_for_annex_symlink (test_ratings_qc.RatingsQc.test_manifest_preserves_source_path_for_annex_symlink) ... ok
test_original_schema_and_missing_subject_are_audited (test_ratings_qc.RatingsQc.test_original_schema_and_missing_subject_are_audited) ... ok
test_repeated_header_selects_validated_final_block (test_ratings_qc.RatingsQc.test_repeated_header_selects_validated_final_block) ... ok
test_archive_preserves_original_and_rejects_links (test_recovery_provenance.RecoveryTest.test_archive_preserves_original_and_rejects_links) ... Imaging-ready runs considered: 10
Task-ready L1 runs: 3
Task-excluded runs: 6
Model-review holds: 1
Task-ready L2 subject-sessions: 3
Ratings-qualified L1 runs: 2
Ratings-qualified L2 subject-sessions: 2
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpvtdb3dkl/l1_task.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpvtdb3dkl/l1_ratings.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpvtdb3dkl/l1_review.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpvtdb3dkl/dispositions.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpvtdb3dkl/l2_task.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpvtdb3dkl/l2_ratings.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpvtdb3dkl/subjects.tsv
ARCHIVED (recoverable): /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp08io9w4o/ds003745/sub-144/old.feat -> /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp08io9w4o/backup/ds003745/sub-144/old.feat
ok
test_cohort_preparation_generates_and_audits_confounds_first (test_recovery_provenance.RecoveryTest.test_cohort_preparation_generates_and_audits_confounds_first) ... ok
test_failed_confounds_audit_prevents_cohort_freeze (test_recovery_provenance.RecoveryTest.test_failed_confounds_audit_prevents_cohort_freeze) ... ok
test_l2_cannot_reuse_stale_l1_parent (test_recovery_provenance.RecoveryTest.test_l2_cannot_reuse_stale_l1_parent) ... ok
test_missing_stamp_old_contrasts_and_changed_inputs_are_rejected (test_recovery_provenance.RecoveryTest.test_missing_stamp_old_contrasts_and_changed_inputs_are_rejected) ... ok
test_selection_is_scoped_and_does_not_restore_excluded_run (test_recovery_provenance.RecoveryTest.test_selection_is_scoped_and_does_not_restore_excluded_run) ... Selected l1: 1 row(s): /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp4icubqfl/selected.tsv
ok
test_source_content_change_invalidates_existing_event_qc (test_recovery_provenance.RecoveryTest.test_source_content_change_invalidates_existing_event_qc) ... ok
test_sub144_requires_verified_repair_but_other_subjects_unchanged (test_recovery_provenance.RecoveryTest.test_sub144_requires_verified_repair_but_other_subjects_unchanged) ... ok
test_audit_requires_complete_matching_bold_and_mask_grids (test_resampling_workflow.ResamplingWorkflow.test_audit_requires_complete_matching_bold_and_mask_grids) ... ok
test_dry_run_validates_manifest_without_writing_outputs (test_resampling_workflow.ResamplingWorkflow.test_dry_run_validates_manifest_without_writing_outputs) ... ok
test_manifest_is_run_level_and_reports_missing_sources (test_resampling_workflow.ResamplingWorkflow.test_manifest_is_run_level_and_reports_missing_sources) ... ok
test_worker_uses_wsinc5_for_bold_and_nn_for_mask (test_resampling_workflow.ResamplingWorkflow.test_worker_uses_wsinc5_for_bold_and_nn_for_mask) ... ok
test_audit_consolidates_complete_result (test_smoothness_workflow.SmoothnessWorkflow.test_audit_consolidates_complete_result) ... ok
test_batch_result_is_atomic_validated_and_restartable (test_smoothness_workflow.SmoothnessWorkflow.test_batch_result_is_atomic_validated_and_restartable) ... ok
test_characterization_manifest_contains_three_required_stages (test_smoothness_workflow.SmoothnessWorkflow.test_characterization_manifest_contains_three_required_stages) ... ok
test_log_tail_is_bounded_and_preserves_diagnostic (test_smoothness_workflow.SmoothnessWorkflow.test_log_tail_is_bounded_and_preserves_diagnostic) ... ok
test_audit_reports_kernel_and_total_target_separately (test_susan_comparison.SusanComparison.test_audit_reports_kernel_and_total_target_separately) ... ok
test_pilot_manifest_selects_highest_baseline_per_dataset (test_susan_comparison.SusanComparison.test_pilot_manifest_selects_highest_baseline_per_dataset) ... ok
test_shell_matches_feat_susan_parameterization (test_susan_comparison.SusanComparison.test_shell_matches_feat_susan_parameterization) ... ok
test_audit_accepts_only_a_bounded_documented_exception (test_target_smoothing_workflow.TargetSmoothingWorkflow.test_audit_accepts_only_a_bounded_documented_exception) ... ok
test_audit_reports_complete_geometry_and_smoothness (test_target_smoothing_workflow.TargetSmoothingWorkflow.test_audit_reports_complete_geometry_and_smoothness) ... ok
test_batch_validates_and_restarts_existing_output (test_target_smoothing_workflow.TargetSmoothingWorkflow.test_batch_validates_and_restarts_existing_output) ... ok
test_manifest_selects_only_analysis_ready_stages_and_owner_paths (test_target_smoothing_workflow.TargetSmoothingWorkflow.test_manifest_selects_only_analysis_ready_stages_and_owner_paths) ... ok

----------------------------------------------------------------------
Ran 61 tests in 24.980s

OK

COMMAND EXIT: 0

CHECK COMMAND: python3 code/verify_neutral_feat_design.py --output logs/records/20260915-retained-contrast-feat-design.json 

PASS: 12 real feat_model cases; full contrast numbering retained, finite matrices, primary contrasts estimable; unsupported neutral contrasts explicitly reported.
Report: logs/records/20260915-retained-contrast-feat-design.json

CHECK EXIT: 0
```
