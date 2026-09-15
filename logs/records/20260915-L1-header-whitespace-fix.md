# L1 scalar-header parsing and worker-error capture

Reviewed `logs/records/sub144-L1-failure-details.txt`, pushed in `2afc07e`.
Both sub-144 runs, for activation and PPI, stopped at `invalid BOLD TR:
2.020000 ` before rendering or launching FEAT. The number is valid; trailing
whitespace from the header command failed the wrapper's anchored regex.

Earlier mock-header tests returned an unpadded value. The real `feat_model`
tests supplied a resolved numerical TR and bypassed the worker's `fslval`
header-reading step. Those validations did not cover this interface.

The worker now trims leading/trailing whitespace from scalar header output
while preserving internal whitespace (so `2 3` remains invalid). Volume count
and TR must be positive; the image/header itself is never changed.

Regression coverage now includes padded spaces/tabs/CR, a 2.02-second TR,
empty/nonpositive/nonnumeric/multiple-token values, and rendering through the
actual installed FSL `fslval` and `fslnvols` when available. That real-tool branch
was exercised successfully on the local Mac during this change.

Both paired launchers now copy the last 80 lines of a failed worker log into
the parent stderr stream, preserving the underlying error in the nohup log
and major Git-tracked run record. Concurrent activation/PPI and failure
propagation tests verify this capture.

Linux2 retry remains pending. Do not interpret local render/header tests as
a completed FEAT fit or completed Linux2 recovery.
