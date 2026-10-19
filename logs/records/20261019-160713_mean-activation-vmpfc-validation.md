# Run Record: mean-activation-vmpfc-validation

- Validation scope: the working-tree implementation committed alongside this record; the commit field below is its parent revision, not a claim that the parent contained these changes.
- Runtime: `/Users/tug87422/fsl/bin/python3`; FSLDIR `/Users/tug87422/fsl`; FSL command directories prepended to PATH; `RUN_FSL_SMOKE=1`; OpenMP/OpenBLAS threads limited to one.
- Result: all 143 tests passed with no skips, including actual FEAT/FLAME1 fits for the mean and interaction families, exact rendered matrix checks, ROI orchestration, and synthetic participant mask/variance attribution. This is local software validation, not the pending Linux2 cohort analysis.
- Timestamp: 20261019-160713
- Branch: main
- Commit: fe40081
- Host: CLA19733
- User: tug87422
- Working directory: `/Users/tug87422/github/sharedreward-aging`
- Raw log: `/Users/tug87422/github/sharedreward-aging/logs/runs/20261019-160713_mean-activation-vmpfc-validation.log`
- Command exit: 0
- Check exit: none
- Summary: CHECK PASSED: age analysis complete (20 signed maps, 15 ROI tests).

## Command

```bash
bash code/validate_workflow.sh 
```

## Log

```text
RUN START: 20261019-160713
PROJECT_ROOT: /Users/tug87422/github/sharedreward-aging
GIT: main fe40081
HOST: CLA19733
USER: tug87422
PWD: /Users/tug87422/github/sharedreward-aging
COMMAND: bash code/validate_workflow.sh 

PASS: bash syntax
PASS: Python syntax
test_curves_and_paired_slopes_match_direct_regressions (test_absolute_rt_age.AbsoluteRTAge.test_curves_and_paired_slopes_match_direct_regressions) ... ok
test_missing_partner_is_not_silently_dropped (test_absolute_rt_age.AbsoluteRTAge.test_missing_partner_is_not_silently_dropped) ... ok
test_exact_policy_and_no_precision_loss (test_age_mask_allowance.AllowanceTests.test_exact_policy_and_no_precision_loss) ... ok
test_opt_in_records_warning_and_preserves_stamp (test_age_mask_allowance.AllowanceTests.test_opt_in_records_warning_and_preserves_stamp) ... ok
test_scope_validation (test_age_mask_allowance.AllowanceTests.test_scope_validation) ... ok
test_source_misses_task_invalid_ratings_and_review_are_distinct (test_analysis_cohort.CohortTest.test_source_misses_task_invalid_ratings_and_review_are_distinct) ... ok
test_batch_and_audit_preserve_tsnr_motion_coverage_contract (test_analysis_qc.AnalysisQc.test_batch_and_audit_preserve_tsnr_motion_coverage_contract) ... ok
test_common_mask_uses_reference_grid_and_nearest_neighbor (test_analysis_qc.AnalysisQc.test_common_mask_uses_reference_grid_and_nearest_neighbor) ... ok
test_coverage_eligible_mask_subtracts_resampled_exemption (test_analysis_qc.AnalysisQc.test_coverage_eligible_mask_subtracts_resampled_exemption) ... ok
test_rf1_motion_qc_uses_named_fmriprep_table_not_feat_matrix (test_analysis_qc.AnalysisQc.test_rf1_motion_qc_uses_named_fmriprep_table_not_feat_matrix) ... ok
test_rf1_is_pinned_to_complete_sharedreward_session_01_inventory (test_characterization_inventory.CharacterizationInventoryTest.test_rf1_is_pinned_to_complete_sharedreward_session_01_inventory) ... ok
test_low_coverage_run_creates_mosaic_and_summary (test_coverage_mosaics.CoverageMosaics.test_low_coverage_run_creates_mosaic_and_summary) ... ok
test_builds_deterministic_runlist_with_exclusions (test_ds003745_runlist.Ds003745Runlist.test_builds_deterministic_runlist_with_exclusions) ... ok
test_strictly_more_than_25pct_excludes_run_not_subject_with_usable_run (test_event_qc.EventQc.test_strictly_more_than_25pct_excludes_run_not_subject_with_usable_run) ... ok
test_decisions_apply_once_and_only_to_pending_rows (test_exclusion_ledger.DecisionFiles.test_decisions_apply_once_and_only_to_pending_rows) ... ok
test_merge_keeps_decisions_notes_and_manual_rows (test_exclusion_ledger.LedgerValidation.test_merge_keeps_decisions_notes_and_manual_rows) ... ok
test_unmatched_and_incomplete_rows_fail (test_exclusion_ledger.LedgerValidation.test_unmatched_and_incomplete_rows_fail) ... ok
test_candidates_repoint_single_run_subjects_to_verified_l1 (test_exclusion_ledger.Resolver.test_candidates_repoint_single_run_subjects_to_verified_l1) ... ok
test_exclusions_drive_strategy_and_rebuilds (test_exclusion_ledger.Resolver.test_exclusions_drive_strategy_and_rebuilds) ... ok
test_ratings_rows_never_remove_runs (test_exclusion_ledger.Resolver.test_ratings_rows_never_remove_runs) ... ok
test_roi_coverage_and_missing_location (test_exclusion_ledger.RoiCoverage.test_roi_coverage_and_missing_location) ... ok
test_reports_complete_and_incomplete_participants (test_fmriprep_audit.FmriprepAudit.test_reports_complete_and_incomplete_participants) ... ok
test_missing_base_column_fails (test_fsl_confounds.FSLConfoundsTest.test_missing_base_column_fails) ... ok
test_rf1_base_policy_and_zero_fill (test_fsl_confounds.FSLConfoundsTest.test_rf1_base_policy_and_zero_fill) ... ok
test_changed_prepared_input_blocks_resume (test_full_analysis.FullAnalysis.test_changed_prepared_input_blocks_resume) ... ok
test_models_are_paired_and_l2_waits_for_l1_audit (test_full_analysis.FullAnalysis.test_models_are_paired_and_l2_waits_for_l1_audit) ... Imaging-ready runs considered: 10
Task-ready L1 runs: 3
Task-excluded runs: 6
Model-review holds: 1
Task-ready L2 subject-sessions: 3
Ratings-qualified L1 runs: 1
Ratings-qualified L2 subject-sessions: 1
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp2yahcu_y/l1_task.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp2yahcu_y/l1_ratings.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp2yahcu_y/l1_review.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp2yahcu_y/dispositions.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp2yahcu_y/l2_task.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp2yahcu_y/l2_ratings.tsv
Wrote: /private/var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp2yahcu_y/subjects.tsv
CHECK PASSED: pooled activation/VS-PPI L1 and subject outputs verified. Cooper QC/L3 decisions remain separate.
ok
test_only_reviewed_models_are_retired_and_recoverable (test_full_analysis.FullAnalysis.test_only_reviewed_models_are_retired_and_recoverable) ... PRESERVED and retired: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp_9fzl8vh/fsl/rf1/sub-10668/ses-01/L1_task-sharedreward_model-fulltrial_type-act_run-1_sm-6.feat -> /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp_9fzl8vh/backup/models/rf1/sub-10668/ses-01/L1_task-sharedreward_model-fulltrial_type-act_run-1_sm-6.feat
PRESERVED and retired: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp_9fzl8vh/fsl/rf1/sub-10668/ses-01/L1_task-sharedreward_model-fulltrial_type-act_run-2_sm-6.feat -> /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp_9fzl8vh/backup/models/rf1/sub-10668/ses-01/L1_task-sharedreward_model-fulltrial_type-act_run-2_sm-6.feat
PRESERVED and retired: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp_9fzl8vh/fsl/rf1/sub-10657/ses-01/L1_task-sharedreward_model-fulltrial_type-act_run-1_sm-6.feat -> /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp_9fzl8vh/backup/models/rf1/sub-10657/ses-01/L1_task-sharedreward_model-fulltrial_type-act_run-1_sm-6.feat
ok
test_repair_selection_requires_both_runs_and_exact_session (test_full_analysis.FullAnalysis.test_repair_selection_requires_both_runs_and_exact_session) ... ok
test_seed_resampling_is_once_per_subject_and_restartable (test_full_analysis.FullAnalysis.test_seed_resampling_is_once_per_subject_and_restartable) ... VS seed caches prepared serially for 1 subjects
VS seed caches prepared serially for 1 subjects
ok
test_unverified_existing_model_blocks_launch (test_full_analysis.FullAnalysis.test_unverified_existing_model_blocks_launch) ... ok
test_contract_is_full_trial_only (test_fulltrial_candidate.Candidate.test_contract_is_full_trial_only) ... ok
test_actual_contrast_matrix_change_fails (test_group_readiness.GroupReadiness.test_actual_contrast_matrix_change_fails) ... ok
test_both_designs_ignore_neutral_and_phys_rows (test_group_readiness.GroupReadiness.test_both_designs_ignore_neutral_and_phys_rows) ... ok
test_cli_one_run_passthrough_and_missing_model_reports (test_group_readiness.GroupReadiness.test_cli_one_run_passthrough_and_missing_model_reports) ... ok
test_event_content_not_just_file_existence (test_group_readiness.GroupReadiness.test_event_content_not_just_file_existence) ... ok
test_l2_fixed_effects_and_parent_identity (test_group_readiness.GroupReadiness.test_l2_fixed_effects_and_parent_identity) ... ok
test_manifests_reject_duplicate_and_changed_retained_runs (test_group_readiness.GroupReadiness.test_manifests_reject_duplicate_and_changed_retained_runs) ... ok
test_neutral_maps_not_required_but_bad_primary_variance_fails (test_group_readiness.GroupReadiness.test_neutral_maps_not_required_but_bad_primary_variance_fails) ... ok
test_nonestimable_primary_fails (test_group_readiness.GroupReadiness.test_nonestimable_primary_fails) ... ok
test_provenance_ignores_deleted_neutral_parent_map_only (test_group_readiness.GroupReadiness.test_provenance_ignores_deleted_neutral_parent_map_only) ... ok
test_selection_uses_coefficients_not_all_label (test_group_readiness.GroupReadiness.test_selection_uses_coefficients_not_all_label) ... ok
test_temporal_ev_filter_fails (test_group_readiness.GroupReadiness.test_temporal_ev_filter_fails) ... ok
test_wrong_affine_and_nonfinite_fail (test_group_readiness.GroupReadiness.test_wrong_affine_and_nonfinite_fail) ... ok
test_ds003745_preserves_published_trial_timing_and_omits_blocks (test_harmonized_events.Events.test_ds003745_preserves_published_trial_timing_and_omits_blocks) ... Wrote 2 ds003745 full-trial rows: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp5mai0zrh/out.tsv
ok
test_rf1_derives_decision_to_outcome_offset_and_miss (test_harmonized_events.Events.test_rf1_derives_decision_to_outcome_offset_and_miss) ... Wrote 2 rf1 full-trial rows: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmp93z4jdg9/out.tsv
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
test_design_no_sex_and_exact_covariates (test_l3_flame.L3Tests.test_design_no_sex_and_exact_covariates) ... ok
test_dof_audit_distinguishes_group_scope_and_reports_all_inputs (test_l3_flame.L3Tests.test_dof_audit_distinguishes_group_scope_and_reports_all_inputs) ... ok
test_interaction_keeps_centered_main_effects_and_exact_contrasts (test_l3_flame.L3Tests.test_interaction_keeps_centered_main_effects_and_exact_contrasts) ... ok
test_pooled_mean_unequal_datasets_and_hc3_intercept (test_l3_flame.L3Tests.test_pooled_mean_unequal_datasets_and_hc3_intercept) ... ok
test_qc_outlier_cannot_enter_retained_manifest (test_l3_flame.L3Tests.test_qc_outlier_cannot_enter_retained_manifest) ... ok
test_ratings_direction_and_rule (test_l3_flame.L3Tests.test_ratings_direction_and_rule) ... ok
test_real_feat_flame1 (test_l3_flame.L3Tests.test_real_feat_flame1) ... ok
test_real_feat_flame1_mean (test_l3_flame.L3Tests.test_real_feat_flame1_mean) ... ok
test_real_feat_model_matrix (test_l3_flame.L3Tests.test_real_feat_model_matrix) ... ok
test_roi_cli_all_families_support_and_completion (test_l3_flame.L3Tests.test_roi_cli_all_families_support_and_completion)
Exercise the ROI orchestration, not only individual statistical helpers. ... Plan: 24 imaging participants; 16 FEAT models; stage=roi
INPUT AUDIT: age_act_cope-10: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_act_cope-11: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_act_cope-12: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_act_cope-14: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_act_cope-16: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_act_cope-17: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_ppi_seed-vs_cope-10: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_ppi_seed-vs_cope-11: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_ppi_seed-vs_cope-12: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_ppi_seed-vs_cope-14: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_ppi_seed-vs_cope-16: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age_ppi_seed-vs_cope-17: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age-ratings_act_cope-17: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age-ratings_ppi_seed-vs_cope-17: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age-ratings-interaction_act_cope-17: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: age-ratings-interaction_ppi_seed-vs_cope-17: 24 inputs; 0 failures; support 48/64 voxels
ROI SAVED: 24 tests; input audit complete=True.
CHECK PASSED: requested FEAT/FLAME1 and/or ROI stage complete.
Plan: 24 imaging participants; 3 FEAT models; stage=roi
INPUT AUDIT: mean_act_cope-10: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: mean_act_cope-11: 24 inputs; 0 failures; support 48/64 voxels
INPUT AUDIT: mean_act_cope-12: 24 inputs; 0 failures; support 48/64 voxels
ROI SAVED: 6 tests; input audit complete=True.
CHECK PASSED: requested FEAT/FLAME1 and/or ROI stage complete.
ok
test_tsnr_retained_only (test_l3_flame.L3Tests.test_tsnr_retained_only) ... ok
test_variance_support_excludes_zeros_not_bad_dof_or_subjects (test_l3_flame.L3Tests.test_variance_support_excludes_zeros_not_bad_dof_or_subjects) ... ok
test_matches_direct_subject_difference_hc3_in_both_models (test_loss_age_differences.LossAgeDifferences.test_matches_direct_subject_difference_hc3_in_both_models) ... ok
test_plot_matches_sex_adjusted_model_and_creates_outputs (test_loss_age_differences.LossAgeDifferences.test_plot_matches_sex_adjusted_model_and_creates_outputs) ... ok
test_interaction_weights_and_covariance_against_explicit_fe (test_next_trial_rt_age.NextTrialRT.test_interaction_weights_and_covariance_against_explicit_fe) ... ok
test_missing_cells_fail (test_next_trial_rt_age.NextTrialRT.test_missing_cells_fail) ... ok
test_selection_does_not_bridge_misses_neutral_or_blocks (test_next_trial_rt_age.NextTrialRT.test_selection_does_not_bridge_misses_neutral_or_blocks) ... ok
test_six_absolute_curves_match_independent_hc3 (test_next_trial_rt_age.NextTrialRT.test_six_absolute_curves_match_independent_hc3) ... ok
test_centering_preserves_paired_comparisons (test_normalized_loss_ratings.NormalizedRatings.test_centering_preserves_paired_comparisons) ... ok
test_six_cell_normalization_and_affine_invariance (test_normalized_loss_ratings.NormalizedRatings.test_six_cell_normalization_and_affine_invariance) ... ok
test_zero_sd_fails_without_dropping_subject (test_normalized_loss_ratings.NormalizedRatings.test_zero_sd_fails_without_dropping_subject) ... ok
test_normalized_gaps_and_direct_difference_prediction (test_normalized_rating_gaps.NormalizedGaps.test_normalized_gaps_and_direct_difference_prediction) ... ok
test_sex_adjustment_toggle_preserves_sample_and_direct_test (test_normalized_rating_gaps.NormalizedGaps.test_sex_adjustment_toggle_preserves_sample_and_direct_test) ... ok
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
test_candidate_order_and_excluded_runs (test_preliminary_age.AgeTests.test_candidate_order_and_excluded_runs) ... ok
test_design_and_hc3 (test_preliminary_age.AgeTests.test_design_and_hc3) ... ok
test_fsl_probability_direction_and_family_correction (test_preliminary_age.AgeTests.test_fsl_probability_direction_and_family_correction) ... ok
test_independent_stage_orchestration_and_provisional_reports (test_preliminary_age.AgeTests.test_independent_stage_orchestration_and_provisional_reports)
Real extraction/statistics/plotting, stubbed external audit/permutations. ... Age analysis plan (roi): 60 people; 60 runs; 0 whole-brain models; 15 ROI tests
Design: ['intercept', 'age_decades_centered', 'dataset_rf1', 'sex_M', 'sex_O', 'retained_mean_fd_centered']; private outputs: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpou5l0t_9/derivatives/preliminary-age/roi; reports: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpou5l0t_9/logs/records/preliminary-age/roi
Prepared act_cope-10: common mask 8 voxels
Prepared act_cope-11: common mask 8 voxels
Prepared act_cope-12: common mask 8 voxels
Prepared act_cope-14: common mask 8 voxels
Prepared act_cope-16: common mask 8 voxels
Prepared ppi_seed-vs_cope-10: common mask 8 voxels
Prepared ppi_seed-vs_cope-11: common mask 8 voxels
Prepared ppi_seed-vs_cope-12: common mask 8 voxels
Prepared ppi_seed-vs_cope-14: common mask 8 voxels
Prepared ppi_seed-vs_cope-16: common mask 8 voxels
CHECK PASSED: ROI age analysis complete (15 tests); no whole-brain permutations requested.
Age analysis plan (wholebrain): 60 people; 60 runs; 10 whole-brain models; 0 ROI tests
Design: ['intercept', 'age_decades_centered', 'dataset_rf1', 'sex_M', 'sex_O', 'retained_mean_fd_centered']; private outputs: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpou5l0t_9/derivatives/preliminary-age/wholebrain; reports: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpou5l0t_9/logs/records/preliminary-age/wholebrain
Prepared act_cope-10: common mask 8 voxels
Prepared act_cope-11: common mask 8 voxels
Prepared act_cope-12: common mask 8 voxels
Prepared act_cope-14: common mask 8 voxels
Prepared act_cope-16: common mask 8 voxels
Prepared ppi_seed-vs_cope-10: common mask 8 voxels
Prepared ppi_seed-vs_cope-11: common mask 8 voxels
Prepared ppi_seed-vs_cope-12: common mask 8 voxels
Prepared ppi_seed-vs_cope-14: common mask 8 voxels
Prepared ppi_seed-vs_cope-16: common mask 8 voxels
DONE: ppi_seed-vs_cope-11
DONE: act_cope-11
DONE: act_cope-12
DONE: act_cope-14
DONE: ppi_seed-vs_cope-12
DONE: act_cope-10
DONE: ppi_seed-vs_cope-10
DONE: ppi_seed-vs_cope-14
DONE: act_cope-16
DONE: ppi_seed-vs_cope-16
CHECK PASSED: age analysis complete (20 signed maps, 0 ROI tests).
Age analysis plan (all): 60 people; 60 runs; 10 whole-brain models; 15 ROI tests
Design: ['intercept', 'age_decades_centered', 'dataset_rf1', 'sex_M', 'sex_O', 'retained_mean_fd_centered']; private outputs: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpou5l0t_9/derivatives/preliminary-age/all; reports: /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpou5l0t_9/logs/records/preliminary-age/all
Prepared act_cope-10: common mask 8 voxels
Prepared act_cope-11: common mask 8 voxels
Prepared act_cope-12: common mask 8 voxels
Prepared act_cope-14: common mask 8 voxels
Prepared act_cope-16: common mask 8 voxels
Prepared ppi_seed-vs_cope-10: common mask 8 voxels
Prepared ppi_seed-vs_cope-11: common mask 8 voxels
Prepared ppi_seed-vs_cope-12: common mask 8 voxels
Prepared ppi_seed-vs_cope-14: common mask 8 voxels
Prepared ppi_seed-vs_cope-16: common mask 8 voxels
DONE: act_cope-11
DONE: act_cope-10
DONE: act_cope-16
DONE: ppi_seed-vs_cope-10
DONE: act_cope-14
DONE: ppi_seed-vs_cope-12
DONE: ppi_seed-vs_cope-11
DONE: act_cope-12
DONE: ppi_seed-vs_cope-14
DONE: ppi_seed-vs_cope-16
CHECK PASSED: age analysis complete (20 signed maps, 15 ROI tests).
ok
test_merged_order_roi_and_coverage (test_preliminary_age.AgeTests.test_merged_order_roi_and_coverage) ... ok
test_rank_failure (test_preliminary_age.AgeTests.test_rank_failure) ... ok
test_endpoint_counts_and_age_boundaries (test_ratings_ceiling.CeilingSensitivity.test_endpoint_counts_and_age_boundaries) ... ok
test_fractional_endpoint_fit_and_paired_delta_covariance (test_ratings_ceiling.CeilingSensitivity.test_fractional_endpoint_fit_and_paired_delta_covariance) ... ok
test_same_sample_and_exact_ols_gap_decomposition (test_ratings_ceiling.CeilingSensitivity.test_same_sample_and_exact_ols_gap_decomposition) ... ok
test_summaries_and_exports (test_ratings_comparison.MatchedFigures.test_summaries_and_exports) ... ok
test_equality_is_allowed_but_loss_greater_than_win_is_excluded (test_ratings_qc.RatingsQc.test_equality_is_allowed_but_loss_greater_than_win_is_excluded) ... ok
test_manifest_preserves_source_path_for_annex_symlink (test_ratings_qc.RatingsQc.test_manifest_preserves_source_path_for_annex_symlink) ... ok
test_original_schema_and_missing_subject_are_audited (test_ratings_qc.RatingsQc.test_original_schema_and_missing_subject_are_audited) ... ok
test_repeated_header_selects_validated_final_block (test_ratings_qc.RatingsQc.test_repeated_header_selects_validated_final_block) ... ok
test_current_cohort_has_six_raw_values_per_person (test_raw_ratings.RawRatings.test_current_cohort_has_six_raw_values_per_person) ... ok
test_gap_predictions_and_paired_slope_tests_use_subject_covariance (test_raw_ratings.RawRatings.test_gap_predictions_and_paired_slope_tests_use_subject_covariance) ... ok
test_holm_preserves_input_order (test_raw_ratings.RawRatings.test_holm_preserves_input_order) ... ok
test_old_cohort_flag_cannot_restore_a_within_partner_violation (test_raw_ratings.RawRatings.test_old_cohort_flag_cannot_restore_a_within_partner_violation) ... ok
test_other_recorded_sex_is_retained_as_category (test_raw_ratings.RawRatings.test_other_recorded_sex_is_retained_as_category) ... ok
test_plot_predictions_match_marginal_fit_and_mean_covariance (test_raw_ratings.RawRatings.test_plot_predictions_match_marginal_fit_and_mean_covariance) ... ok
test_wide_fit_matches_subject_contrast_and_preserves_age_effect (test_raw_ratings.RawRatings.test_wide_fit_matches_subject_contrast_and_preserves_age_effect) ... ok
test_within_partner_rule_allows_ties_not_compensating_wins (test_raw_ratings.RawRatings.test_within_partner_rule_allows_ties_not_compensating_wins) ... ok
test_archive_preserves_original_and_rejects_links (test_recovery_provenance.RecoveryTest.test_archive_preserves_original_and_rejects_links) ... ARCHIVED (recoverable): /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpl2p83dry/ds003745/sub-144/old.feat -> /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpl2p83dry/backup/ds003745/sub-144/old.feat
ok
test_cohort_preparation_generates_and_audits_confounds_first (test_recovery_provenance.RecoveryTest.test_cohort_preparation_generates_and_audits_confounds_first) ... ok
test_failed_confounds_audit_prevents_cohort_freeze (test_recovery_provenance.RecoveryTest.test_failed_confounds_audit_prevents_cohort_freeze) ... ok
test_l2_cannot_reuse_stale_l1_parent (test_recovery_provenance.RecoveryTest.test_l2_cannot_reuse_stale_l1_parent) ... ok
test_missing_stamp_old_contrasts_and_changed_inputs_are_rejected (test_recovery_provenance.RecoveryTest.test_missing_stamp_old_contrasts_and_changed_inputs_are_rejected) ... ok
test_selection_is_scoped_and_does_not_restore_excluded_run (test_recovery_provenance.RecoveryTest.test_selection_is_scoped_and_does_not_restore_excluded_run) ... Selected l1: 1 row(s): /var/folders/k2/d1bh9qd5753_9sj9b62rfzwm0000gp/T/tmpeh93y_9q/selected.tsv
ok
test_source_content_change_invalidates_existing_event_qc (test_recovery_provenance.RecoveryTest.test_source_content_change_invalidates_existing_event_qc) ... ok
test_sub144_requires_verified_repair_but_other_subjects_unchanged (test_recovery_provenance.RecoveryTest.test_sub144_requires_verified_repair_but_other_subjects_unchanged) ... ok
test_audit_requires_complete_matching_bold_and_mask_grids (test_resampling_workflow.ResamplingWorkflow.test_audit_requires_complete_matching_bold_and_mask_grids) ... ok
test_dry_run_validates_manifest_without_writing_outputs (test_resampling_workflow.ResamplingWorkflow.test_dry_run_validates_manifest_without_writing_outputs) ... ok
test_manifest_is_run_level_and_reports_missing_sources (test_resampling_workflow.ResamplingWorkflow.test_manifest_is_run_level_and_reports_missing_sources) ... ok
test_worker_uses_wsinc5_for_bold_and_nn_for_mask (test_resampling_workflow.ResamplingWorkflow.test_worker_uses_wsinc5_for_bold_and_nn_for_mask) ... ok
test_10657_only_run1 (test_reviewed_10657.ReviewedDisposition.test_10657_only_run1) ... ok
test_features_preserve_missing_switches_in_older_dataset (test_rt_switch_ratings.RTSwitchRatings.test_features_preserve_missing_switches_in_older_dataset) ... ok
test_folds_and_training_only_scaling (test_rt_switch_ratings.RTSwitchRatings.test_folds_and_training_only_scaling) ... ok
test_ratings_hc3_matches_statsmodels (test_rt_switch_ratings.RTSwitchRatings.test_ratings_hc3_matches_statsmodels) ... ok
test_switch_contrasts_against_explicit_fixed_effect_regression (test_rt_switch_ratings.RTSwitchRatings.test_switch_contrasts_against_explicit_fixed_effect_regression) ... ok
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
test_absorbed_matches_explicit_fixed_effects_and_cluster_covariance (test_trial_behavior.TrialBehavior.test_absorbed_matches_explicit_fixed_effects_and_cluster_covariance) ... ok
test_event_count_mismatch_fails (test_trial_behavior.TrialBehavior.test_event_count_mismatch_fails) ... ok
test_misses_and_block_boundaries_are_not_bridged (test_trial_behavior.TrialBehavior.test_misses_and_block_boundaries_are_not_bridged) ... ok
test_attribution_frequencies_and_unchanged_sources (test_vmpfc_support.CoverageTests.test_attribution_frequencies_and_unchanged_sources) ... ok
test_cli_and_plot (test_vmpfc_support.CoverageTests.test_cli_and_plot) ... ok
test_fail_on_nonfinite_mismatch_duplicate_and_adapter (test_vmpfc_support.CoverageTests.test_fail_on_nonfinite_mismatch_duplicate_and_adapter) ... ok

----------------------------------------------------------------------
Ran 143 tests in 183.550s

OK

COMMAND EXIT: 0
```
