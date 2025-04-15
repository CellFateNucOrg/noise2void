import argparse
import os
from os.path import join, isdir, basename
from os import makedirs
from bioio import BioImage
from matplotlib import pyplot as plt
import numpy as np
from n2v.models import N2V
from image_utils import *

os.environ['TF_XLA_FLAGS'] = '--tf_xla_enable_xla_devices'

def split_nd(img_dir, img_name, channel_list, model_base_dir, project=True):
	denoised_dir = join(img_dir, basename(model_base_dir), 'denoised')
	if not isdir(denoised_dir):
		makedirs(denoised_dir, exist_ok=True) # Make a directory for the denoised images if it does not exist yet
	img = join(img_dir, img_name)
	dims = ''.join([i for i in ['T', 'C'] if BioImage(img).dims[i][0] > 1])
	tcz_path = split_stack(img, dims=dims, keep_img=True) # Split images by time point and/or channel
	temp_path = join(denoised_dir, f'{img_name[:img_name.rfind(".")]}_temp.zarr')
	root = zarr.group(store=temp_path)
	for i in range(len(channel_list)): # Loop over the channels defined in the .sh file
		to_denoise = []
		groups, arrays = unpack_zarr(tcz_path)
		for array in arrays:
			if 'c' + str(i).zfill(3) in array:
				to_denoise.append(array)
		for array in to_denoise:
			data = zarr.open_array(array)
			denoised_data = n2v_denoise(data=data,
			img_dir=img_dir,
			img_name=img_name,
			model_base_dir=model_base_dir,
			channel=channel_list[i],
			plotInputPredict=True
			)
			root.array(name=f'{basename(array)}_n2v', data=denoised_data)
	stack_paths = stack_images(imgs=temp_path, dims=dims, keep_imgs=False)	
	for path in stack_paths:
		print(f'project is set to {project}')
		print(type(project))
		tif_path = zarr_to_tif(zarr_file=path, keep_img=False)
		print(tif_path)
		if project == True:
			print('True')
			print(tif_path)
			project_image(tif_path)
		else:
			print('NO')
	shutil.rmtree(tcz_path)

def n2v_denoise(data, img_dir, img_name, model_base_dir, channel, plotInputPredict=False):
	model = N2V(config=None, name=channel, basedir=model_base_dir) # Load the trained model
	# Pass the input image (a numpy array) to the denoising function
	# T and C of the input have a size of one already and are specified only to reduce the shape of the array from 5D to 3D
	# n_tiles is to split up the image in case it is too big for the RAM and will be set automatically if not specified
	denoised_data = model.predict(data[0, 0], axes='ZYX', n_tiles=(1, 4, 4))
	if(plotInputPredict): # Plot a flattened image of both the input and the predited (i.e., denoised) image
		inputpredict_dir = join(img_dir, basename(model_base_dir), 'inputPredict')
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
		plt.savefig(join(inputpredict_dir, "InputPredict_" + img_name[0 : img_name.rfind(".")] + '_' + channel + '.tif'))
	denoised_data = np.expand_dims(np.expand_dims(denoised_data, axis=0), axis=0) # This is to makes sure the image stays 5D
	return denoised_data

def get_args(): # Parse arguments from the shell script
	parser = argparse.ArgumentParser()
	parser.add_argument("-d", "--img_dir", help="Path to directory containing the images to denoise", type=str, required=True)
	parser.add_argument("-i", "--img_name", help="Name of image to denoised", type=str, required=True)
	parser.add_argument("-c", "--channel_list", action="extend", nargs="+", type=str, help="Ordered list of channel names", required=True, default=[])
	parser.add_argument("-m", "--model_base_dir", help="Path to directory containing the models", type=str, required=True)
	parser.add_argument("-p", "--project", help="Whether to save a projection of each denoised image", type=bool, required=True)
	return parser.parse_args()

def main():
	img_dir = get_args().img_dir
	img_name = get_args().img_name
	channel_list = get_args().channel_list
	model_base_dir = get_args().model_base_dir
	project = get_args().project
	split_nd(img_dir=img_dir,
	img_name=img_name,
	channel_list=channel_list,
	model_base_dir=model_base_dir,
	project=project
	) # Split stacks by timepoints and/or channels

if __name__=='__main__':
	main()
