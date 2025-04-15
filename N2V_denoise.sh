#!/bin/bash
#SBATCH --time=1-0:00:00
#SBATCH --mem 64GB
#SBATCH --ntasks=8
#SBATCH --gres=gpu:1

IMG_DIR=
MODEL_BASE_DIR=
CHANNEL_LIST=(red green)
PROJECT=True

source $HOME/miniforge3/bin/activate n2v

FILE_LIST=(`ls ${IMG_DIR}`)

for IMG_NAME in ${FILE_LIST[@]}
do
  echo "Processing" $IMG_NAME
  python ./Scripts/N2Vdenoise.py -d $IMG_DIR -i $IMG_NAME -m $MODEL_BASE_DIR -c ${CHANNEL_LIST[@]} -p $PROJECT
done
