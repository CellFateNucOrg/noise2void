# Use this script to start the denoising
# 'IMG_DIR', 'MODEL_BASE_DIR', and 'CHANNEL_LIST' must be specified

#!/bin/bash
#SBATCH --time=0-10:00:00
#SBATCH --mem 128GB
#SBATCH --gres=gpu:1

IMG_DIR=
# This is the directory containing the raw images you want to denoise
# If the files are are loaded from a mounted drive, make sure to replace 'Volumes' with 'mnt'

MODEL_BASE_DIR=
# This is the directory containing folders for the individual channels to train the model on
# If the files are are loaded from a mounted drive, make sure to replace 'Volumes' with 'mnt'

CHANNEL_LIST=(red green)
# 'CHANNELS' should is a list (separated by spaces) containing all the channels to denoise
# For each item in 'CHANNELS', there should be a folder in 'MODEL_BASE_DIR' containing a model

source $HOME/miniforge3/bin/activate n2v

FILE_LIST=(`ls ${IMG_DIR}`)

for IMG_NAME in ${FILE_LIST[@]}
do
  echo "Processing" $IMG_NAME
  python ./N2Vdenoise.py -d $IMG_DIR -i $IMG_NAME -c ${CHANNEL_LIST[@]} -m $MODEL_BASE_DIR
done
