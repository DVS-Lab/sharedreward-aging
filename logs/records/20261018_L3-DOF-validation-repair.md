# L3 DOF validation and ROI checkpoint repair

Reviewed production run: `L3-FLAME1-age-ratings-20261018-224232`.
The readiness stage verified 1,326 L1 and 716 subject-level models under the
recorded provisional policy. The command then exited 1 before any FEAT model
launch. The earlier readiness `CHECK PASSED` was not a successful L3 run.
No new complete ROI/rating results or FLAME1 age maps were produced by that run.

The exception arose from the launcher's requirement for positive DOF at every
voxel in each individual input mask. The error lacked source and voxel details.
Production DOF maps are on Linux2, not in the local clone, so their precise
problem remains to be established by the new diagnostic.

Local FSL `featlib.tcl` constructs the higher-level mask by intersecting input
masks and masks the merged DOF images before FLAMEO. The launcher now checks
DOF positivity within that same intersection. It preserves original masks,
DOF maps, contrasts, exclusions, subject membership and model covariates.
Nonpositive DOF inside the intersection remains a failure. The fitted FEAT
mask must also equal the audited intersection.

Every input is inspected before launching any whole-brain models. Tracked
per-model diagnostics identify source files, mask voxel counts, DOF ranges,
and nonpositive DOF inside versus outside the group mask. Missing fixed-effects
DOF maps still fail; no DOF replacement or mask trimming was introduced.

ROI tables and plots now finish and are saved before whole-brain preparation,
with a separate completion record. This preserves the requested age and
ratings ROI analyses if DOF inspection blocks whole-brain execution again.

Validation on the local FSL installation:

- Full suite: 110 tests, successful, one opt-in real FEAT test skipped.
- Separate real-FSL suite: seven tests passed, including FEAT/FLAME1 with zero
  DOF inside individual masks but outside the group intersection. Fitted
  mask, design, contrasts, statistics and cluster outputs were verified.
- Regression diagnostic: outside-common zeros pass; inside-common zeros and
  missing fixed-effects DOF files fail and all failures are recorded.

No production Linux2 images or old run outputs were changed. A new labeled
Linux2 launch is required to obtain the corrected diagnostics and results.
