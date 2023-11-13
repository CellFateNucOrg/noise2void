#!/bin/bash
#SBATCH --time=0-05:00:00
#SBATCH --mem 256GB
#SBATCH --gres=gpu:1

IMAGE_DIR=/mnt/external.data/MeisterLab/jsemple/microscopy/20230907_941-9_SMCGFP1_HS
CHANNEL_NAME=green
MODEL_BASE_NAME=n2v_3D_CREST_

source $HOME/miniforge3/bin/activate n2v

python ./trainN2Vmodel.py --image_dir $IMAGE_DIR --channel_name $CHANNEL_NAME --model_base_name $MODEL_BASE_NAME

