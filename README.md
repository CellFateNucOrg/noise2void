# noise2void
Scripts for performing noise2void denoising of microscopy images 

## Installing environment
First be sure you have conda or [mamba](https://mamba.readthedocs.io/en/latest/mamba-installation.html) installed. I will give the commands with mamba, but you can simply subsittute the word conda for mamba.

To be sure we can install the gpu enabled versions of software we should ssh into the gpu server izbdelhi.
Then create an interactive job with the gpu:

```
salloc -w izbdelhi --mem 16GB --time 1:00:00 --gres=gpu:1
```

The installation essentially uses the instructions from the [n2v](https://github.com/juglab/n2v) github repository and [tensorflow](https://www.tensorflow.org/install/pip) page, as well as some other packages.

Create a mamba environment:

```
mamba create -n "n2v" python=3.9
mamba activate n2v
mamba install -c conda-forge nd2reader scikit-image jupyter
```

Install tensorflow with pip (cuda should already be installed on izbdelhi

```
pip install tensorflow
```

Make the path available as per tensorflow docs:

```
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
```

Install n2v with pip

```
pip install n2v
```

There may be some packages i have forgotten - complete docs when try new installation. Try to

When finished, cancel the gpu job on the server (using scancel jobid).

## Pulling scripts from github
Change directory (cd) and go to the directory with the images. Then initiate a github repo, set the origin to this repository and fetch the scripts.

```
git init
git remote add origin git@github.com:CellFateNucOrg/noise2void.git
git fetch
git checkout -t origin/main
```
This may not work. in which case delete the .git folder. then create a new folder by cloning the repository adn then move the images into that folder

## Train model

Every new type of image with different type of flourophore and distribution requires initial training of the n2v model. These scripts are designed for .nd2 images from the CREST with 1 or more fluorophores (each needs to be trained separately) and z-stacks. time series might need tweeking.

### Setup for training

Before strating you need to interactively choose a region of a single slice of one of your images with the typical signal and background. The **getTrainingRegion.ijm** macro will help you do that in fiji.
Open one of your images, go to a central z-slice and then run the macro: drag the macro file into fiji and it will open the code window, then click "run". the macro will enhance contrast and then create a square of the right size which you should move to a region that contains your signal of interest and background (don't change the size of the square).
Once you have selected the region and click "continue", the macro will separate channels and create tiffs of this square for training. Save them with an *_\<channelName\>.tif* suffix (where *\<channelName\>* is e.g. green).

Go to the directory where you have your images and create a directory for the training images, e.g. if you have green and red channels:

```
mkdir -p n2v_denoise/training/green
mkdir -p n2v_denoise/training/red
```

Place the images created with the fiji macro into their respective directories

### Training
ssh into izbdelhi so you can use the GPU.

Open the **00_trainModel_n2v.sh** script and modify the full path to the directory where you have you images (IMAGE_DIR variable).

Modify the name of the channel (CHANNEL_NAME variable) you wish to train, you need to run the script separately for each channel - this is the same name as you used in the setup for training above.

You may wish to modify the   MODEL_BASE_NAME if you are doing anything other than a 3d CREST image.

You might need to change the path to the environment you created if you are using conda and not mamba

Close the script and submit as sbatch job:

```
sbatch 00_trainModel_n2v.sh
```

Training should take 2-3 hours

When training is finished, examine the *trainingValidationLoss_n2v_3D_CREST_\<channelName\>.png* file in the *n2v_denoise/training/\<channelName\>* directory. It should look like this:
![training validation](https://github.com/CellFateNucOrg/noise2void/blob/main/n2v_denoise/training/green/trainingValidationLoss_n2v_3D_CREST_green.png?raw=true)

The blue and orange lines should converge. if they do not you can increase the number of epochs you use for training by modifying the **trainN2Vmodel.py** script and the repeat the training.

### Denoising
Once you have finished training models for all the channels you can use them to denoise the rest of the images of that type.

ssh into izbdelhi so you can use the GPU.

Open the **01_denoise_n2v.sh** script and modify the path to the directory with the .nd2 format images you want to denoise (IMAGE_DIR), and the path to the models you trained (MODEL_DIR). This could be in a subdirectory of the IMAGE_DIR, or if you repeatedly image the same fluorescent protein you can use a model you already trained (which is why this is a separate variable).

Use the same model base name as you used in the training.

CHANNEL_LIST should include all the channels you trained models for e.g. (green red). The list must be in the same order the channels appear in your image. 

You might need to change the path to activate your environment if you are using conda and not mamba.

Close the script and submit as sbatch job:

```
sbatch 01_denoise_n2v.sh
```

The denoised images will be in the *n2v_denoise/denoised* folder





