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
RUN_TYPES=("act" "ppi_seed-vs")

# ROI dictionary: "source_cluster_mask | lo_thr | hi_thr"
# Mask created with: fslmaths <source> -thr <lo> -uthr <hi> -bin <out>
# Use "premade" for masks that already exist in maskdir
# ROI keys are suffixed with figure number to disambiguate same anatomy across figures

declare -A ROI_PARAMS
ROI_PARAMS["dlpfc-fig4"]="${fsldir}/L3act/L3_model-age_task-${TASK}_n${N}_flame1/L3_task-${TASK}_type-act_cnum-14_cname-rew-pun_F-S_${GROUP}.gfeat/cope1.feat/cluster_mask_zstat1.nii.gz | 1 | 1"
ROI_PARAMS["mpfc-fig5"]="${fsldir}/L3act/L3_model-Fwin-Floss_Swin-Sloss_task-${TASK}_n${N}_flame1/L3_task-${TASK}_type-act_cnum-14_cname-rew-pun_F-S_${GROUP}.gfeat/cope1.feat/cluster_mask_zstat7.nii.gz | 1 | 1"
ROI_PARAMS["vs-mpfc-fig6"]="${fsldir}/L3ppi_seed-vs/L3_model-Fwin-Floss_Swin-Sloss_task-${TASK}_n${N}_flame1/L3_task-${TASK}_type-ppi_seed-vs_cnum-14_cname-rew-pun_F-S_${GROUP}.gfeat/cope1.feat/cluster_mask_zstat8.nii.gz | 2 | 2"
ROI_PARAMS["dlpfc-fig7"]="${fsldir}/L3act/L3_model-age_task-${TASK}_n${N}_flame1/L3_task-${TASK}_type-act_cnum-10_cname-rew-pun_${GROUP}.gfeat/cope1.feat/cluster_mask_zstat3.nii.gz | 1 | 1"
#ROI_PARAMS["vmpfc-fig8"]="${fsldir}/L3act/L3_model-age_task-${TASK}_n${N}_flame1/L3_task-${TASK}_type-act_cnum-10_cname-rew-pun_${GROUP}.gfeat/cope1.feat/cluster_mask_zstat3.nii.gz | 1 | 1"
ROI_PARAMS["vmpfc-fig9"]="${fsldir}/L3act/L3_model-age_task-${TASK}_n${N}_flame1/L3_task-${TASK}_type-act_cnum-18_cname-pun_F-S_${GROUP}.gfeat/cope1.feat/cluster_mask_zstat4.nii.gz | 1 | 1"
ROI_PARAMS["left-dls-fig10"]="${fsldir}/L3act/L3_model-age_task-${TASK}_n${N}_flame1/L3_task-${TASK}_type-act_cnum-17_cname-rew_F-S_${GROUP}.gfeat/cope1.feat/cluster_mask_zstat1.nii.gz | 6 | 6"
ROI_PARAMS["right-dls-fig11"]="${fsldir}/L3act/L3_model-age_task-${TASK}_n${N}_flame1/L3_task-${TASK}_type-act_cnum-17_cname-rew_F-S_${GROUP}.gfeat/cope1.feat/cluster_mask_zstat1.nii.gz | 1 | 1"
ROI_PARAMS["seed-vs-fig3"]="premade"

# Cope dictionary: "model_key|copenum" -> copename

declare -A COPE_PARAMS
COPE_PARAMS["model-age|01"]="C_pun"
COPE_PARAMS["model-age|02"]="C_rew"
COPE_PARAMS["model-age|03"]="F_pun"
COPE_PARAMS["model-age|04"]="F_rew"
COPE_PARAMS["model-age|05"]="S_pun"
COPE_PARAMS["model-age|06"]="S_rew"
COPE_PARAMS["model-age|10"]="rew-pun"
COPE_PARAMS["model-age|17"]="rew_F-S"
COPE_PARAMS["model-age|18"]="pun_F-S"


COPE_PARAMS["model-Fwin-Floss_Swin-Sloss|14"]="rew-pun_F-S"

# Figure dictionary: "ROI|model_key|TYPE|copenum" -> figure number
# This is the single source of truth for what gets extracted
declare -A FIGURE_MAP
FIGURE_MAP["dlpfc-fig4|model-age|act|01"]="4"
FIGURE_MAP["dlpfc-fig4|model-age|act|02"]="4"
FIGURE_MAP["dlpfc-fig4|model-age|act|03"]="4"
FIGURE_MAP["dlpfc-fig4|model-age|act|04"]="4"
FIGURE_MAP["dlpfc-fig4|model-age|act|05"]="4"
FIGURE_MAP["dlpfc-fig4|model-age|act|06"]="4"

FIGURE_MAP["seed-vs-fig3|model-age|act|01"]="3"
FIGURE_MAP["seed-vs-fig3|model-age|act|02"]="3"
FIGURE_MAP["seed-vs-fig3|model-age|act|03"]="3"
FIGURE_MAP["seed-vs-fig3|model-age|act|04"]="3"
FIGURE_MAP["seed-vs-fig3|model-age|act|05"]="3"
FIGURE_MAP["seed-vs-fig3|model-age|act|06"]="3"
FIGURE_MAP["seed-vs-fig3|model-age|act|10"]="3"

FIGURE_MAP["mpfc-fig5|model-Fwin-Floss_Swin-Sloss|act|14"]="5"

FIGURE_MAP["vs-mpfc-fig6|model-Fwin-Floss_Swin-Sloss|ppi_seed-vs|14"]="6"

FIGURE_MAP["dlpfc-fig7|model-age|act|10"]="7"

FIGURE_MAP["vmpfc-fig9|model-age|act|18"]="9"

FIGURE_MAP["left-dls-fig10|model-age|act|01"]="10"
FIGURE_MAP["left-dls-fig10|model-age|act|02"]="10"
FIGURE_MAP["left-dls-fig10|model-age|act|03"]="10"
FIGURE_MAP["left-dls-fig10|model-age|act|04"]="10"
FIGURE_MAP["left-dls-fig10|model-age|act|05"]="10"
FIGURE_MAP["left-dls-fig10|model-age|act|06"]="10"
FIGURE_MAP["left-dls-fig10|model-age|act|17"]="10"

FIGURE_MAP["right-dls-fig11|model-age|act|01"]="11"
FIGURE_MAP["right-dls-fig11|model-age|act|02"]="11"
FIGURE_MAP["right-dls-fig11|model-age|act|03"]="11"
FIGURE_MAP["right-dls-fig11|model-age|act|04"]="11"
FIGURE_MAP["right-dls-fig11|model-age|act|05"]="11"
FIGURE_MAP["right-dls-fig11|model-age|act|06"]="11"
FIGURE_MAP["right-dls-fig9|model-age|act|17"]="11"


create_masks() {
    for ROI in "${!ROI_PARAMS[@]}"; do
        if [[ "${ROI_PARAMS[$ROI]}" == "premade" ]]; then
            echo "Using premade mask for ${ROI}"
            continue
        fi

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
    for key in "${!FIGURE_MAP[@]}"; do
        IFS='|' read -r ROI model_key TYPE copenum <<< "$key"

        if [[ ${#RUN_TYPES[@]} -gt 0 ]]; then
            match=0
            for allowed in "${RUN_TYPES[@]}"; do
                [[ "$TYPE" == "$allowed" ]] && match=1 && break
            done
            [[ $match -eq 0 ]] && continue
        fi

        fig="${FIGURE_MAP[$key]}"
        copename="${COPE_PARAMS["${model_key}|${copenum}"]}"
        MASK="${maskdir}/${ROI}.nii.gz"

        if [[ ! -f "$MASK" ]]; then
            echo "WARNING: mask not found for ${ROI}, skipping."
            continue
        fi

        L3_DIR="${fsldir}/L3${TYPE}/L3_${model_key}_task-${TASK}_n${N}_flame1"
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

        VAR_DATA="${L3_DIR}/L3_task-${TASK}_type-${TYPE}_cnum-${copenum}_cname-${copename}_${GROUP}.gfeat/cope1.feat/var_filtered_func_data.nii.gz"
        VAR_OUT="${figdir}/${ROI}_${model_key}_type-${TYPE}_cope-${copenum}_cname-${copename}_var.txt"

        if [[ ! -f "$VAR_DATA" ]]; then
            echo "WARNING: variance data not found: ${VAR_DATA}"
        else
            echo "Extracting variance: ${ROI} | ${model_key} | ${TYPE} | cope-${copenum} (${copename}) -> figure-${fig}"
            fslmeants -i "$VAR_DATA" -o "$VAR_OUT" -m "$MASK"
        fi
    done
}

create_masks
extract_timeseries
