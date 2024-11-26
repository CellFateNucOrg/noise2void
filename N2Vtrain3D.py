from os import environ
from os.path import join, basename, dirname
import numpy as np
from n2v.models import N2VConfig, N2V
from csbdeep.utils import plot_history
from n2v.utils.n2v_utils import manipulate_val_data
from n2v.internals.N2V_DataGenerator import N2V_DataGenerator
import matplotlib.pyplot as plt
import argparse
import ssl

environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'
ssl._create_default_https_context = ssl._create_unverified_context

def n2v_train(model_base_dir, channel):
	datagen = N2V_DataGenerator()
	train_imgs = join(model_base_dir, channel, 'train_imgs')
	imgs = datagen.load_imgs_from_directory(directory=train_imgs, dims='ZYX')
	# Split each training image into 3D patches to be used for either training or validation
	# Patch shape must be a common divisor of the size of the training images so the patches will not overlap
	patch_shape = (32, 64, 64)
	patches = datagen.generate_patches_from_list(imgs[:1], shape=patch_shape)
	# Split the patches into a training and a validation set
	patches_tot = len(patches)
	train_patches = patches[:int(patches_tot * 0.8)]
	val_patches = patches[int(patches_tot * 0.8):]
	
	# Define a configuration file for the training
	config = N2VConfig(
		train_patches,
		unet_kern_size=3, 
		train_steps_per_epoch=200, # Increasing training steps may yield better results but at the price of longer computation
		train_epochs=75, # The number of epochs is sufficient if the training & validation plot becomes flat, i.e., the models does not improve much further
		train_loss='mse',
		batch_norm=True, 
		train_batch_size=32,
		n2v_perc_pix=0.198,
		n2v_patch_shape=(32, 64, 64), 
		n2v_manipulator='uniform_withCP',
		n2v_neighborhood_radius=5
	)
	model = N2V(config=config, name=channel, basedir=model_base_dir) # Create a network model for the training
	history = model.train(train_patches, val_patches) # Train the model
	print(sorted(list(history.history.keys())))

	# Plot training and validation loss
	plt.figure(figsize=(16,5))
	plot_history(history, ['loss', 'val_loss'])
	plt.savefig(join(model_base_dir, channel, basename(model_base_dir) + channel + '_plot.png'))

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--model_base_dir", required=True)
	parser.add_argument("-c", "--channel", required=True)
	return parser.parse_args()

def main():
	model_base_dir = get_args().model_base_dir
	channel = get_args().channel
	n2v_train(model_base_dir, channel) # Train the model

if __name__ == '__main__':
	main()