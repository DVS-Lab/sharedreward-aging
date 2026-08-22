# Generated derivatives

Large outputs are ignored:

- `fmriprep/`: modern ds003745 fMRIPrep 25.2.5 derivatives;
- `events/`: model-specific harmonized full-trial TSVs;
- `harmonized/`: ds003745 images resampled to the RF1 grid and later target-smoothed;
- `fsl/`: ds003745 EVs and FEAT trees;
- `qc/`: grid, smoothness, tSNR, motion, coverage, and harmonization tables.

OpenNeuro source BIDS is never overwritten. RF1 FEAT trees remain in `rf1-sra-sharedreward` and are referenced through an explicit root.
