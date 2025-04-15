#!/bin/bash
#SBATCH --time=2-0:00:00
#SBATCH --mem 64GB
#SBATCH --gres=gpu:rtx6000:1

MODEL_BASE_DIR=/mnt/external.data/MeisterLab/Dario/Imaging/Code/N2V/myo3_halo
CHANNELS=(red green)

source $HOME/miniforge3/bin/activate n2v

for CHANNEL in ${CHANNELS[@]}
do
  echo "Training" ${CHANNEL} "channel"
  python ./N2Vtrain3D.py --model_base_dir $MODEL_BASE_DIR --channel $CHANNEL
done
