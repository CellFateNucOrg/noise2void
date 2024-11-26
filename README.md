# noise2void
Scripts for denoising multi-dimensional (up to 5D) microscopy images using noise2void. Based on scripts by Lucien Hinderling (Pertz group) and scripts provided in the [noise2void](https://github.com/juglab/n2v) respository. Instructions below follow those in a [previous fork](https://github.com/CellFateNucOrg/noise2void/tree/jenny_v1) with scripts for denoising 3D images.

## Installation
First be sure you have conda or [mamba](https://mamba.readthedocs.io/en/latest/mamba-installation.html) installed. I will give the commands with mamba, but you can simply subsitute *conda* for *mamba*.The installation essentially uses the instructions from the [n2v](https://github.com/juglab/n2v) repository and [tensorflow](https://www.tensorflow.org/install/pip) page, as well as some other packages.

To be able to install the gpu-enabled versions of the required packages, fist ssh into the gpu node izbdelhi.
Next create a mamba environment and install the packages required to process the images.
```
mamba create -n "n2v" python=3.9
mamba activate n2v
pip install bioio bioio_tifffile bioio_nd2 bioio_czi bioio_lif matplotlib numpy
```

Next install tensorflow. Cuda and tensorflow need to be compatible with gpu software on server. First check what version is installed using the *nvidia-smi* command. Look up compatible versions here: https://www.tensorflow.org/install/source#tested_build_configurations
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
In case this does not work, delete the .git folder and clone the repository from github instead.

## Train a model
Ideally, you should train an individual model for each unique combination of promoter, gene of interest, and fluorophore. You should also train a separate model whenever you image a strain with (significantly) changed acquisition parameters.

### Set up directories
Before you start the training, set up the directories for your model. Personally, I sort all of my images into a parent folder for each strain with sub-folders for each imaging session. Inside the parent directory, I then create a a folder for the model to be trained. This folder should contain a sub-folder for each channel you want to train (for example, named *red* and *green*), each of which should contain sub-folder named *train_imgs*. 

If you want to reuse a model (for example because you have more than one strain with the same marker), copy the folder containing the model for that channel (e.g., *green*) to the new model directory.

### Create training samples
To start the training, you have to provide at least one sample slice from one of your raw images. To this end, open an image of your choice in Fiji. It is important **not** to check the *Use virtual stack* for this! In case the image is a z-stack, move to one of the central planes.

Next run the **getTrainingRegion.ijm** macro and select a representative area of your image, containing both signal and some background. You should not change the size of the selection square nor adjust brightness and contrast. After you confirming your selection, the macro will create a copy of the selected area for each channel. Save those images with a *_<channel_name>.tif* suffix into the correct *train_imgs* folder.

### Training
Depending on whether your training images 2D or 3D files, open the *N2Vtrain2D.sh* or *N2Vtrain3D.sh* script. On macOS, you can open *.sh* files with TextEdit and on Windows using Notepad.

In the *.sh* file you shold adjust the following parameters: *MODEL_BASE_DIR* should be the path to your model (which contains the folders for the individual channels). *CHANNELS* should be a space-separated list with all the channels you want to train. The names of these channels should be identical with the folders inside the *MODEL_BASE_DIR* folder.

After saving the script, ssh into the *izblisbon* node and navigate to the *N2V* folder. Then submit the scripts as an *sbatch* job:
```
sbatch N2Vtrain2D.sh # if your training images are 2D
sbatch N2Vtrain3D.sh # if your training images are 3D
```

The training will usually take between 2 and 3 hours. Afterwards, you can examine the output plot, named *\<model>_\<channel>_plot.png* in the channel sub-folder of the model directory. The blue and orange lines should flatten and converge towards the end of the training. If this is not the case, you can increase the number of epochs in the *N2Vtrain2D.py* or *N2Vtrain3D.py* script and the repeat the training. However, doing so will not always make that big of a difference. Moreover, even if the plot does not look great, quite often the denoising will still yield a good result.

### Denoising
Once the training has finished (and the plots look fine), you can start denoising your raw images. For this, open the *N2Vdenoise.sh* file. Modify *IMG_DIR*, which should point to the folder containing your raw images. *MODEL_BASE_DIR* and *CHANNEL_LIST* should be the same as in the corresponding *N2Vtrain2D.sh* or *N2Vtrain3D.sh* script.

Next ssh into izblisbon, navigate to the *N2V* folder, and submit the script:
```
sbatch N2Vdenoise.sh
```

After the denoising is finished, you will find the denoised images in the *N2V/denoised* sub-directory of the *IMG_PATH*.

# IMPORTANT!
You can use the denoised image to better detect objects and create masks. But remember that then any intensity measurements should be performed on the raw images!!!

