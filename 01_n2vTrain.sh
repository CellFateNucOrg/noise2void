#!/bin/bash
#SBATCH --time=0-05:00:00
#SBATCH --mem 32GB
#SBATCH --gres=gpu:1

TRAIN_DIR=/mnt/external.data/MeisterLab/Dario/Imaging/
MODEL_BASE_NAME=n2v_
CHANNEL_NAME=

source $HOME/miniforge3/bin/activate n2v

python ./n2vTrain.py --train_dir $TRAIN_DIR --channel_name $CHANNEL_NAME --model_base_name $MODEL_BASE_NAME

