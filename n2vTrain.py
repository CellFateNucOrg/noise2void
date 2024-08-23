from n2v.models import N2VConfig, N2V
import numpy as np
import re
from csbdeep.utils import plot_history
from n2v.utils.n2v_utils import manipulate_val_data
from n2v.internals.N2V_DataGenerator import N2V_DataGenerator
from matplotlib import pyplot as plt
import urllib
import os
import zipfile
import argparse
os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'


import ssl
ssl._create_default_https_context = ssl._create_unverified_context

def trainModel_n2v(train_dir, channel_name, model_base_name='n2v_'):
	# We create our DataGenerator-object.
	# It will help us load data and extract patches for training and validation.
	datagen = N2V_DataGenerator()
	# We will load all the '.tif' files from the 'data' directory. In our case it is only one.
	# The function will return a list of images (numpy arrays).
	# In the 'dims' parameter we specify the order of dimensions in the image files we are reading.
	imgs = datagen.load_imgs_from_directory(directory = train_dir + 'train_imgs' + channel_name + '/', dims='ZYX')
	print(f"Dimensions: {imgs[0].shape}")
	# The function automatically added two extra dimension to the images:
	# One at the front is used to hold a potential stack of images such as a movie.
	# One at the end could hold color channels such as RGB.
	
	# Here we extract patches for training and validation.
	patch_shape = (32, 64, 64)
	patches = datagen.generate_patches_from_list(imgs[:1], shape=patch_shape)
	# Patches are created so they do not overlap.
	# Note: this is not the case if you specify a number of patches. See the docstring for details!
	# Non-overlapping patches enable us to split them into a training and validation set.
	# We split the data into a training and validation set. (80% / 20% respectively)	
	nb_patches = len(patches)
	X = patches[:int(nb_patches*0.8)]
	X_val = patches[int(nb_patches*0.8):]
	print(f"Number of patches: {nb_patches}")
	print(f"Patches used for training: {len(X)}")
	print(f"Patches used for validation: {len(X_val)}")

	# You can increase "train_steps_per_epoch" to get even better results at the price of longer computation. 
	config = N2VConfig(X, unet_kern_size=3, 
					   train_steps_per_epoch=200,train_epochs=75, train_loss='mse', batch_norm=True, 
					   train_batch_size=32, n2v_perc_pix=0.198, n2v_patch_shape=(32, 64, 64), 
					   n2v_manipulator='uniform_withCP', n2v_neighborhood_radius=5)

	# Let's look at the parameters stored in the config-object.
	vars(config)
	# a name used to identify the model
	model_name = model_base_name + '_' + channel_name
	# the base directory in which our model will live
	modelDir = train_dir + '/models'
	# We are now creating our network model.
	model = N2V(config=config, name=model_name, basedir=modelDir)

	#Training
	history = model.train(X, X_val)
	#plot training and validation loss
	print(sorted(list(history.history.keys())))
	plt.figure(figsize=(16,5))
	plot_history(history,['loss','val_loss'])
	plt.savefig(train_dir + channel_name +  '/Plot' + model_name + '.png')

	#Export Model in BioImage ModelZoo Forma
	model.export_TF(name='Noise2Void-3DCREST-'+channel_name, 
					description='This is the 3D Noise2Void example trained in python.', 
					authors=["Tim-Oliver Buchholz", "Alexander Krull", "Florian Jug"],
					test_img=X_val[0,...,0], axes='ZYX',
					patch_shape=patch_shape)
	return


def setupDirsForTraining(train_dir, channel_name):
	'''
	Creates directory structure required for training.
	Creates subdirectory within the train_dir called n2v_denoise where training data
	and models will be stored. 
	'''
	# create a folder for our data
	# os.chdir(train_dir)
	# train_channel=os.path.join(train_dir, channel_name)
	# if not os.path.isdir(train_channel):
	#	os.mkdir(train_channel)
	#	print("created " + train_channel)

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("--image_dir", required=True)

	return parser.parse_args()


def main():
	args=get_args()
	train_dir=args.train_dir
	channel_name=args.channel_name
	model_base_name=args.model_base_name
	print("setting up directories")
	setupDirsForTraining(train_dir,channel_name)
	print("starting training")
	trainModel_n2v(train_dir,channel_name, model_base_name)
	

if __name__=='__main__':
	main()
	
