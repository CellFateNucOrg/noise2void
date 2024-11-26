# noise2void
Scripts for denoising multi-dimensional (up to 5D) microscopy images using noise2void. Based on scripts by Lucien Hinderling (Pertz group) and scripts provided in the [noise2void](https://github.com/juglab/n2v) respository. Instructions below follow those in a [previous fork](https://github.com/CellFateNucOrg/noise2void/tree/jenny_v1) with scripts for denoising 3D images.

## Installation
First be sure you have conda or [mamba](https://mamba.readthedocs.io/en/latest/mamba-installation.html) installed. I will give the commands with mamba, but you can simply subsitute 'conda' for 'mamba'.The installation essentially uses the instructions from the [n2v](https://github.com/juglab/n2v) repository and [tensorflow](https://www.tensorflow.org/install/pip) page, as well as some other packages.

To be able to install the gpu-enabled versions of the required packages, fist ssh into the gpu node izbdelhi.
Next create a mamba environment and install the packages required to process the images.
```
mamba create -n "n2v" python=3.9
mamba activate n2v
pip install bioio bioio_tifffile bioio_nd2 bioio_czi bioio_lif matplotlib numpy
```

Next install tensorflow. Cuda and tensorflow need to be compatible with gpu software on server. First check what version is installed using the 'nvidia-smi' command. Look up compatible versions here: https://www.tensorflow.org/install/source#tested_build_configurations
```
mamba install -c conda-forge cudatoolkit=11.8.0
python3 -m pip install nvidia-cudnn-cu11==8.6.0.163 tensorflow[and-cuda]==2.13.0
```

Make the path available as per tensorflow docs:
```
mkdir -p $CONDA_PREFIX/etc/conda/activate.d
echo 'CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
echo 'export LD_LIBRARY_PATH=$CUDNN_PATH/lib:$CONDA_PREFIX/lib/:$LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
source $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
```

Verify that the installation worked:
```
python3 -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"
```
This should return a tensor, something like: "[PhysicalDevice(name='/physical_device:GPU:0', device_type='GPU'), PhysicalDevice(name='/physical_device:GPU:1', device_type='GPU')]". Ignore the warnings about AVX2 and tensorrt.

Next install the n2v package:
```
pip install n2v
```

## Pull scripts from github
Change directory (cd) to where you want to save the scripts. Then initiate a github repo, set the origin to this repository and fetch the scripts:
```
git init
git remote add origin git@github.com:CellFateNucOrg/noise2void.git
git fetch
git checkout -t origin/dario_v2
```
In case this does not work, delete the .git folder and clone the repository from github.

## Train a model
Ideally, you should train an individual model for each unique combination of promoter, gene of interest, and fluorophore. You should also train a separate model whenever you image a strain with (significantly) changed acquisition parameters.

### Set up directories
Before you start the training, set up the directories for your model. Personally, I sort all of my images into a parent folder for a given strain and sub-folder for each imaging session. Inside the parent directory I then create a a folder for the model to be trained. The model directory should contain a sub-folder for each channel you would like to train (for example, named *red* and *green*), each of which should contain another sub-folder named *train_imgs*. 

### Create training samples
To start the training, you have to provide at least one sample slice from one of your raw images. To this end, open an image of your choice in Fiji. It is important **not** to check the 'Use virtual stack' for this! In case the image is a z-stack, move to one of the central planes.

Next run the **getTrainingRegion.ijm** macro and select a representative area of your image, containing both signal and some background. You should not change the size of the selection square nor adjust brightness and contrast. After you confirming your selection, the macro will create a copy of the selected area for each channel. Save those images with a *_<channel_name>.tif* suffix into the correct *train_imgs* folder.

### Training
Depending on whether your training images 2D or 3D files, open the *N2Vtrain2D.sh* or *N2Vtrain*D.sh* script. On macOS, you can open *.sh* files with TextEdit and on Windows with Notepad.

In the *.sh* file you shold adjust the following parameters: *MODEL_BASE_DIR* should be the path to your model (which contains the folders for the individual channels). *CHANNELS* should be a space-separated list with all the channels you want to train. The names of these channels should be identical with the folders inside the *MODEL_BASE_DIR* folder.

After saving the script, ssh into the *izblisbon* node and navigate to the *N2V* folder. Then submit the scripts as an *sbatch* job:
```
sbatch N2Vtrain2D.sh # if your training images are 2D
sbatch N2Vtrain3D.sh # if your training images are 3D
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


# IMPORTANT!
You can use the denoised image to better detect objects and create masks. But remember that then any intensity measurements should be performed on the raw images!!!

