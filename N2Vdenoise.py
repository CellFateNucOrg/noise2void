import argparse
import os
from os.path import join, isdir, basename, dirname
from os import makedirs
from bioio import BioImage
from tifffile import imread, imwrite
from matplotlib import pyplot as plt
import numpy as np
from n2v.models import N2V
from utils import split_stack, stack_imgs

os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'

def split_nd(img_dir, img_name, channel_list, model_base_dir):
	denoised_dir = join(img_dir, 'N2V/denoised')
	if not isdir(denoised_dir):
		makedirs(denoised_dir, exist_ok=True) # Make a directory for the denoised images if it does not exist yet
	img = BioImage(join(img_dir, img_name))
	c = img.dims['C']
	dims = ''.join([i for i in ['T', 'C'] if img.dims[i][0] > 1])
	imgs = split_stack(join(img_dir, img_name), dims=dims) # Split images by time point and/or channel
	denoised_imgs = {}
	for channel in channel_list: # Loop over the channels defined in the .sh file
		to_denoise = {} # Make a dictionary for the images to denoise
		for c in range(len(channel_list)):
			if channel_list[c] == channel:
				channel_no = c # Number the channels in 'channel_list'
			for img in imgs.items():
				if('c' + str(channel_no).zfill(3) in img[0]):
					to_denoise[img[0]] = imgs[img[0]] # Add images to 'to_denoise' based on their 'c' and/or 't' suffix
			for img in to_denoise.items():
				denoised_imgs[img[0]] = n2v_denoise(img[1], img_dir, img_name, model_base_dir, channel, plotInputPredict=True) # Denoise the images and then add them to the 'denoised_imgs' dict
	stack = stack_imgs(denoised_imgs, dims=dims) # Stack the denoised images back together...
	path = join(denoised_dir, img_name[0:img_name.rfind('.')] + '_n2v.tif')
	BioImage(next(iter(stack.items()))[1]).save(path) # ...and save them

def n2v_denoise(data, img_dir, img_name, model_base_dir, channel, plotInputPredict=False):
	model = N2V(config=None, name=channel, basedir=model_base_dir) # Load the trained model
	# Pass the input image (a numpy array) to the denoising function
	# T and C of the input have a size of one already and are specified only to reduce the shape of the array from 5D to 3D
	# n_tiles is to split up the image in case it is too big for the RAM and will be set automatically if not specified
	denoised_data = model.predict(data[0, 0], axes='ZYX', n_tiles=(1, 4, 4))
	if(plotInputPredict): # Plot a flattened image of both the input and the predited (i.e., denoised) image
		inputpredict_dir = join(img_dir,'N2V/inputPredict')
		if not isdir(inputpredict_dir):
			makedirs(inputpredict_dir, exist_ok=True)
		plt.figure(figsize=(30, 30))
		plt.subplot(1, 2, 1) # Plot the input image...
		plt.imshow(
			np.max(data[0, 0], axis=0), 
			cmap = 'gray',
			vmin = np.percentile(data, 0.1),
			vmax = np.percentile(data, 99.9))
		plt.title('Input');
		plt.subplot(1, 2, 2) # ...and the denoised one
		plt.imshow(
			np.max(denoised_data, axis=0),
			cmap = 'gray',
			vmin = np.percentile(denoised_data, 0.1),
			vmax = np.percentile(denoised_data, 99.9))
		plt.title('Prediction')
		plt.savefig(join(inputpredict_dir, "InputPredict_" + img_name[0 : img_name.rfind('.')] + '_' + channel + '.tif'))
	denoised_data = np.expand_dims(np.expand_dims(denoised_data, axis=0), axis=0) # This is to makes sure the image stays 5D
	return denoised_data

def get_args(): # Parse arguments from the shell script
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--img_dir", help="Path to directory containing nd2 images", type=str, required=True)
	parser.add_argument("-i", "--img_name", help="Name of nd2 image to be processed", type=str, required=True)
	parser.add_argument("-c", "--channel_list", action="extend", nargs="+", type=str, help="Ordered list of channel names", required=True, default=[])
	parser.add_argument("-m", "--model_base_dir", help="Path to directory containing the models", type=str, required=True)
	return parser.parse_args()

def main():
	img_dir = get_args().img_dir
	img_name = get_args().img_name
	channel_list = get_args().channel_list
	model_base_dir = get_args().model_base_dir
	split_nd(img_dir, img_name, channel_list, model_base_dir) # Split stacks by timepoints and/or channels

if __name__=='__main__':
	main()
