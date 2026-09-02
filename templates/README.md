# Templates

Historical FEAT/FLOBS/PPI/L3 templates are retained for audit and as the source of unchanged FEAT settings. They are not overwritten. `code/render_pooled_fsf.py` applies a deterministic narrow transform at run time: FEAT smoothing becomes zero, the missed-trial EV uses the same double-gamma convolution as the other task regressors, unsupported decision EVs/contrasts are removed, and the tracked full-trial contrast vectors are installed. All other FEAT settings come from the existing templates.

The approved pooled model is a common full-trial event model with nine partner × feedback conditions and an optional missed-trial nuisance EV. It deliberately omits separate decision regressors because ds003745 does not support equivalent exact phase timing. The 28 activation contrasts are defined in `FULLTRIAL_CONTRAST_CANDIDATE.tsv`; PPI uses the same 28 vectors on the interaction EVs plus one physiological contrast.

The ds003745 block rows support a dataset-specific block sensitivity model. A block-level pooled model requires a scientifically defensible RF1 analogue and is not assumed here.
