# Use this script to train 3D images
# 'MODEL_BASE_DIR' and 'CHANNEL_LIST' must be specified

#!/bin/bash
#SBATCH --time=0-05:00:00
#SBATCH --mem 32GB
#SBATCH --gres=gpu:rtx6000:1

MODEL_BASE_DIR=
# This is the directory containing folders for the individual channels to train the model on
# If the files are are loaded from a mounted drive, make sure to replace 'Volumes' with 'mnt'

CHANNELS=(red green)
# 'CHANNELS' should is a list (separated by spaces) containing all the channels to train
# For each item in 'CHANNELS', there should be a folder in 'MODEL_BASE_DIR' containing a model

source $HOME/miniforge3/bin/activate n2v

for CHANNEL in ${CHANNELS[@]}
do
  echo "Training" ${CHANNEL} "channel"
  python ./N2Vtrain3D.py --model_base_dir $MODEL_BASE_DIR --channel $CHANNEL
done