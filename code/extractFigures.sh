#!/usr/bin/env bash

# Paths
scriptdir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
maindir="$(dirname "$scriptdir")"
maskdir="${maindir}/masks"
outputdir="${maindir}/derivatives/imaging_plots"
fsldir="${maindir}/derivatives/fsl"
mkdir -p "$outputdir"

# Study parameters
TASK="sharedreward"
GROUP="onegroup"
N=288

# Seeds only used when TYPE is ppi_seed-<seed>
SEEDS=(ofc vmpfc dlpfc vs)

# Types to run: act, melodic-nppi-dmn, or ppi_seed-<seed> (expanded from SEEDS)
TYPES=("act" "melodic-nppi-dmn")
for seed in "${SEEDS[@]}"; do
    TYPES+=("ppi_seed-${seed}")
done

# Limit to specific types, or leave empty to run all
RUN_TYPES=("act")

# ROI dictionary: "source_cluster_mask | lo_thr | hi_thr"
# Mask created with: fslmaths <source> -thr <lo> -uthr <hi> -bin <out>
# Note that the cluster indices should always be the same number within ROI_PARAM calls
declare -A ROI_PARAMS
ROI_PARAMS["dlpfc"]="${fsldir}/L3act/L3_model-age_task-${TASK}_n${N}_flame1/L3_task-${TASK}_type-act_cnum-14_cname-rew-pun_F-S_${GROUP}.gfeat/cope1.feat/cluster_mask_zstat1.nii.gz | 1 | 1"

# Cope dictionary: "model_key|copenum" -> copename
declare -A COPE_PARAMS
COPE_PARAMS["model-age|03"]="F_pun"
COPE_PARAMS["model-age|04"]="F_rew"
COPE_PARAMS["model-age|05"]="S_pun"
COPE_PARAMS["model-age|06"]="S_rew"

# Figure dictionary: "ROI|model_key|TYPE|copenum" -> figure number
# Any combination not listed here will be skipped with a warning
declare -A FIGURE_MAP
FIGURE_MAP["dlpfc|model-age|act|03"]="4"
FIGURE_MAP["dlpfc|model-age|act|04"]="4"
FIGURE_MAP["dlpfc|model-age|act|05"]="4"
FIGURE_MAP["dlpfc|model-age|act|06"]="4"

create_masks() {
    for ROI in "${!ROI_PARAMS[@]}"; do
        IFS='|' read -r source_mask lo_thr hi_thr <<< "${ROI_PARAMS[$ROI]}"
        source_mask="${source_mask// /}"
        lo_thr="${lo_thr// /}"
        hi_thr="${hi_thr// /}"
        out_mask="${maskdir}/${ROI}.nii.gz"

        echo "Creating mask: ${ROI} (thr: ${lo_thr} and ${hi_thr})"
        fslmaths "$source_mask" -thr "$lo_thr" -uthr "$hi_thr" -bin "$out_mask"
    done
}

extract_timeseries() {
    for TYPE in "${TYPES[@]}"; do
        if [[ ${#RUN_TYPES[@]} -gt 0 ]]; then
            match=0
            for allowed in "${RUN_TYPES[@]}"; do
                [[ "$TYPE" == "$allowed" ]] && match=1 && break
            done
            [[ $match -eq 0 ]] && continue
        fi

        for ROI in "${!ROI_PARAMS[@]}"; do
            MASK="${maskdir}/${ROI}.nii.gz"
            if [[ ! -f "$MASK" ]]; then
                echo "WARNING: mask not found for ${ROI}, skipping."
                continue
            fi

            for cope_key in "${!COPE_PARAMS[@]}"; do
                IFS='|' read -r model_key copenum <<< "$cope_key"
                copename="${COPE_PARAMS[$cope_key]}"

                fig="${FIGURE_MAP["${ROI}|${model_key}|${TYPE}|${copenum}"]}"
                if [[ -z "$fig" ]]; then
                    echo "WARNING: no figure mapping for ${ROI}|${model_key}|${TYPE}|${copenum}, skipping."
                    continue
                fi

                L3_DIR="${fsldir}/L3act/L3_${model_key}_task-${TASK}_n${N}_flame1"
                DATA="${L3_DIR}/L3_task-${TASK}_type-${TYPE}_cnum-${copenum}_cname-${copename}_${GROUP}.gfeat/cope1.feat/filtered_func_data.nii.gz"

                if [[ ! -f "$DATA" ]]; then
                    echo "WARNING: data not found: ${DATA}"
                    continue
                fi

                figdir="${outputdir}/figure-${fig}"
                mkdir -p "$figdir"
                OUT="${figdir}/${ROI}_${model_key}_type-${TYPE}_cope-${copenum}_cname-${copename}.txt"
                echo "Extracting: ${ROI} | ${model_key} | ${TYPE} | cope-${copenum} (${copename}) -> figure-${fig}"
                fslmeants -i "$DATA" -o "$OUT" -m "$MASK"
            done
        done
    done
}

create_masks
extract_timeseries
