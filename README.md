# noise2void
Scripts for performing noise2void denoising of microscopy images 

## Installing environment
First be sure you have conda or [mamba](https://mamba.readthedocs.io/en/latest/mamba-installation.html)) installed. I will give the commands with mamba, but you can simply subsittute the word conda for mamba.

To be sure we can install the gpu enabled versions of software we should ssh into the gpu server izbdelhi.
Then create an interactive job with the gpu:
'''
salloc -w izbdelhi --mem 16GB --time 1:00:00 --gres=gpu:1
'''

The installation essentially uses the instructions from the [n2v](https://github.com/juglab/n2v) github repository and [tensorflow](https://www.tensorflow.org/install/pip) page, as well as some other packages.

Create an mamba environment:
'''
mamba create -n "n2v" python=3.9
mamba activate n2v1
mamba install -c conda-forge nd2 scikit-image
'''

Install tensorflow with pip
'''
python3 -m pip install tensorflow[and-cuda]
'''

Make the path available as per tensorflow docs:
'''
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
'''

Install some n2v and some other packages with pip:
'''
pip install n2v jupyter
'''

There may be some packages i have forgotten - complete docs when try new installation. Try to

when finished, cancel the gpu job on the server (using scancel jobid).

## Train model

Every new type of image with different type of flourophore and distribution requires initial training of the n2v model. These scripts are designed for .nd2 images from the CREST with 1 or more fluorophores (each needs to be trained separately) and z-stacks. time series might need tweeking.

### Setup for training

Before strating you need to interactively choose a region of a single slice of one of your images with the typical signal and background. The **getTrainingRegion.ijm** macro will help you do that in fiji.
Open one of your images, go to a central z-slice and then run the macro: drag it to into fiji and it will open the code window, then click "run". the macro will enhance contrast and then create a square of the right size which you should move to a region that contains your signal of interest and background.
Once you have selected the region and click "continue?", the macro will separate channels and create tiffs of this square for training. Save them with an _channelName.tif suffix.
(where channelName is e.g. green)

Go to the directory where you have your images and create a directory for the training images, e.g. if you have green and red channels:
'''
mkdir -p n2v_denoise/training/green
mkdir -p n2v_denoise/training/red
'''
Place the images created with the fiji macro into their respective directories

### Training
ssh into izbdelhi so you can use the GPU.

Open the **00_trainModel_n2v.sh** script and modify the full path to the directory where you have you images (IMAGE_DIR variable).

Modify the name of the channel (CHANNEL_NAME variable) you wish to train, you need to run the script separately for each channel - this is the same name as you used in the setup for training above.

You may wish to modify the   MODEL_BASE_NAME if you are doing anything other than a 3d CREST image.

You might need to change the path to the environment you created if you are using conda and not mamba

Close the script and submit an sbatch job:
'''
sbatch 00_trainModel_n2v.sh
'''

Training should take 2-3 hours

When training is finished, examine the trainingValidationLoss_n2v_3D_CREST_channelName.png file in the n2v_denoise/training/channelName directory. It should look like this:
![training validation](https://github.com/CellFateNucOrg/noise2void/blob/main/n2v_denoise/training/green/trainingValidationLoss_n2v_3D_CREST_green.png?raw=true)

### 



