#!/bin/bash
#SBATCH --time=0-05:00:00
#SBATCH --mem 32GB
#SBATCH --gres=gpu:1

IMAGE_DIR=/mnt/external.data/MeisterLab/Dario/Imaging/SDC1/1273/1273_02/
MODEL_DIR=/mnt/external.data/MeisterLab/Dario/Imaging/SDC1/1273/n2v_1273G_1268R/models
MODEL_BASE_NAME=n2v_1273G_1268R
CHANNEL_LIST=(red green)

source $HOME/miniforge3/bin/activate n2v

# use some expression to get list of files to process 
FILE_LIST=(`ls ${IMAGE_DIR}/*.nd2 | grep -v _bf.nd2`)

for IMAGE_NAME in ${FILE_LIST[@]}
do
  echo "processing " $IMAGE_NAME
  python ./n2vDenoise.py -d $IMAGE_DIR -i $IMAGE_NAME -m $MODEL_DIR -n $MODEL_BASE_NAME -c ${CHANNEL_LIST[@]} 
done
