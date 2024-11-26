from os.path import isfile, basename
import re
import numpy as np
from bioio import BioImage

def scale_img(img, bits=(1, 1), dtype=np.float16):
    """Scale an image.
    
    Parameters
    ----------
    img : numpy.ndarray or image
        Image to normalise.
    bits : (2) sequence of ints, optional, default (1, 1)
        Bit depth of the input and output data, respectively.
    dtype: numpy.dtype, optional, default numpy.float16
        Data type of the output array.

    Returns
    -------
    scal_data : numpy.ndarray
        Scaled data.

    """
    img = BioImage(img)
    data = img.data
    try:
        import numexpr as ne
        scal_data = (ne.evaluate('data / (2**bits[0] - 1) * (2**bits[1] - 1)')).astype(dtype=dtype)
    except:
        scal_data = (data / (2**bits[0] - 1) * (2**bits[1] - 1)).astype(dtype=dtype)
    return scal_data

def normalise_img(img, pths=(0, 100), pxls=None, bits=12, dtype=np.float16):
    """Normalise an image by percentiles or pixel values.
    
    Parameters
    ----------
    img : numpy.ndarray or image
        Image to normalise.
    pths : (2) sequence of ints, optional, default (0, 100)
        Minimum and maximum percentile, respectively.
    pxls : (2) sequence of ints, optional, default None
        Minimum and maximum pixel value, respectively. If set, percentiles will be ignored.
    bits : int, optional, default 12
        Bit depth of the output image.
    dtype: numpy.dtype, optional, default numpy.float16
        Data type of the output array.

    Returns
    -------
    norm_data : numpy.ndarray
        Normalised data.

    """
    img = BioImage(img)
    data = img.data
    max_px = np.percentile(data, pths[0], axis=None) if pxls[0] == None else pxls[0]
    min_px = np.percentile(data, pths[1], axis=None) if pxls[1] == None else pxls[1]
    try:
        import numexpr as ne
        norm_data = (ne.evaluate('(data - min_px) / (max_px - min_px) * (2**bits - 1)')).astype(dtype=dtype)
    except:
        norm_data = ((data - min_px) / (max_px - min_px) * (2**bits - 1)).astype(dtype=dtype)
    return norm_data

def project_img(img, dim='Z', proj='max'):
    """Project an image.
    
    Parameters
    ----------
    img : numpy.ndarray or image
        Image to project.
    dim : {'T', 'C', 'Z', 'X', 'Y'}, optional, default 'Z'
        Dimension in which to project the stack.
    proj : {'max', 'min', 'mean', 'median', 'sum'}, optional, default 'max'
        Type of projection to perform.
    
    Returns
    -------
    proj_data : numpy.ndarray
        Projected data.

    """
    img = BioImage(img)
    raw_data = img.data
    axis = 'TCZYX'.index(dim)
    if proj == 'min':
        proj_data = raw_data.min(axis=axis, keepdims=True)
    elif proj == 'max':
        proj_data = raw_data.max(axis=axis, keepdims=True)
    elif proj == 'mean':
        proj_data = raw_data.mean(axis=axis, keepdims=True)
    elif proj == 'median':
        proj_data = np.median(raw_data, axis=axis, keepdims=True)
    elif proj == 'sum':
        proj_data = raw_data.sum(axis=axis, keepdims=True)
    return proj_data

def reshape_img(img, shape):
    """Reshape the dimensions of an image.

    Parameters
    ----------
    img : numpy.ndarray or image
        Image to reshape.
    shape : sequence of ints
        Shape of the output image. Must be compatible with the shape of the input image.
    Returns
    -------
    resh_data : numpy.ndarray
        Reshaped data.

    """
    img = BioImage(img)
    data = img.data
    resh_data = data.reshape(shape)
    return resh_data

def order_dims(img, dims, order='TCZYX'):
    """Reorder the dimensions of an image.

    Parameters
    ----------
    img : numpy.ndarray or image
        Image to reorder.
    dims : str of 'T', 'C', 'Z', 'X', 'Y'
        Order of dimensions of the input image. Must compatible with the dimensions of the output image.
    order :  str of 'T', 'C', 'Z', 'X', 'Y', optional, default 'TCZYX'
        Order of dimensions of the output image. Must compatible with the dimensions of the input image.

    Returns
    -------
    ord_data : numpy.ndarray
       Reordered data.

    """
    img = BioImage(img)
    data = img.data
    add_dims = [order.index(i) for i in order if i not in dims]
    data = np.expand_dims(data, add_dims)
    unord_dims = [order.index(i) for i in dims]
    ord_dims = sorted(unord_dims)
    ord_data = np.moveaxis(data, unord_dims, ord_dims)
    return ord_data

def split_stack(img, dims='C'):
    """Split an image stack into seperate images.
    
    Parameters
    ----------
    img : numpy.ndarray or image
        Image stack to split up.
    dims : str of 'T', 'C', 'Z', optional, default 'C'
        Dimension(s) in which to split the image stack.

    Returns
    -------
    imgs : dict[str, numpy.ndarray]
        Names and data of the split images. File names indicate the position of the image in the input stack.

    """
    name = basename(img) if isfile(img) else ''
    img = BioImage(img)
    data = img.data
    t, c, z = img.dims['T', 'C', 'Z']
    imgs = {}
    dim = dims[0]
    idx = [f'_{dim.lower()}{str(i).zfill(3)}' for i in range(img.dims[dim][0])]
    if len(dims) > 1:
        for i in range(1, len(dims)):
            dim = dims[i]
            temp = []
            for j in idx:
                for k in [f'_{dim.lower()}{str(k).zfill(3)}' for k in range(img.dims[dim][0])]:
                    temp.append(f'{j}{k}')
        idx = temp
    for i in range(len(idx)):
        new_img = f'{name[0:name.rfind(".")]}{idx[i]}'
        ti = re.search(f'_t\\d+', idx[i])
        t1 = int(ti.group()[2:]) if bool(ti) else 0
        t2 = t1 + 1 if bool(ti) else t
        ci = re.search(f'_c\\d+', idx[i])
        c1 = int(ci.group()[2:]) if bool(ci) else 0
        c2 = c1 + 1 if bool(ci) else c
        zi = re.search(f'_z\\d+', idx[i])
        z1 = int(zi.group()[2:]) if bool(zi) else 0
        z2 = z1 + 1 if bool(zi) else z
        imgs[new_img] = data[t1:t2, c1:c2, z1:z2, ...]
    return imgs

def stack_imgs(imgs, dims='C'):
    """Stack images into a single file.

    Parameters
    ----------
    imgs : sequence of images or dict[str, numpy.ndarray]
        Images to stack. File names must include a string of 'c', 't', 'x', 'y', 'z' and integers indicating the position of the image in the output stack.
    dims : str of 'T', 'C', 'Z', optional, default 'C'
        Dimension(s) in which to stack the images.

    Returns
    -------
    stacks : dict[str, numpy.ndarray]
        Name and data of the output stack.

    """
    if isinstance(imgs, list) or isinstance(imgs, tuple):
        imgs = {basename(img) : BioImage(img).data for img in imgs if isfile(img)}
    imgs = dict(sorted(imgs.items()))
    stacks = {}
    dim = dims[0]
    axis = 'TCZ'.index(dim)
    for img in imgs.items():
        name, data = img[0], img[1]
        add_dims = [i for i in range(5 - (len(data.shape)))]
        data = np.expand_dims(data, add_dims)
        new_stack = re.sub(f'_{dim.lower()}\\d+', '', name)
        if not new_stack in stacks:
            stacks[new_stack] = [data]
        else:
            stacks[new_stack].append(data)
    for stack in stacks:
        stacks[stack] = np.concatenate(stacks[stack], axis=axis)
    if len(dims) > 1:
        for i in range(1, len(dims)):
            temp = {}
            del_stacks = []
            dim = dims[i]
            axis = 'TCZ'.index(dim)
            for stack in stacks.items():
                name, data = stack[0], stack[1]
                new_stack = re.sub(f'_{dim.lower()}\\d+', '', name)
                if not new_stack in temp:
                    temp[new_stack] = [data]
                else:
                    temp[new_stack].append(data)
                del_stacks.append(name)
            for stack in temp:
                temp[stack] = np.concatenate(temp[stack], axis=axis)
            stacks.update(temp)
            for stack in del_stacks:
                stacks.pop(stack)
    return stacks

def translate_img(img, channel=0, shift=(0, 0, 0)):
    """Translate an image in 2D or 3D.

    Parameters
    ----------
    img : numpy.ndarray or image
        Image to translate.
    channel : int, optional, default 0
        Channel to shift.
    shift : (3) sequence of ints, optional, default (0, 0, 0)
        Distance in pixels in x, y, and z, respectively.

    Returns
    -------
    trans_data : numpy.ndarray
        Translated data.
        
    """
    img = BioImage(img)
    raw_data = img.data
    t, c, z, y, x = img.dims['T', 'C', 'Z', 'Y', 'X']
    x_shift, y_shift, z_shift = shift
    trans_data = np.empty(shape=(t, c, z - abs(z_shift), y - abs(y_shift), x - abs(x_shift)))
    for i in range(c):
        x1 = abs(x_shift) if (i == channel and x_shift < 0) or (i != channel and x_shift > 0) else 0
        x2 = x - abs(x_shift) if (i == channel and x_shift > 0) or (i != channel and x_shift < 0) else x + 1
        y1 = abs(y_shift) if (i == channel and y_shift < 0) or (i != channel and y_shift > 0) else 0
        y2 = y - abs(y_shift) if (i == channel and y_shift > 0) or (i != channel and y_shift < 0) else y + 1
        z1 = abs(z_shift) if (i == channel and z_shift < 0) or (i != channel and z_shift > 0) else 0
        z2 = z - abs(z_shift) if (i == channel and z_shift > 0) or (i != channel and z_shift < 0) else z + 1
        trans_data[:, i:i+1, ...] = raw_data[:, i:i+1, z1:z2, y1:y2, x1:x2]
    return trans_data

def correct_img(raw_img, flat_img, dark_img, roi=None, bits=12, dtype=np.float16):
    """Perform a flat-field correction.

    Parameters
    ----------
    raw_img : numpy.ndarray or image
        Image to correct.
    flat_image : numpy.ndarray or image
        Flat-field image.
    dark_image : numpy.ndarray or image
        Dark image.
    roi : (4) sequence of ints, optional, default None
        ROI of the input image. Integers should indicate the distance in pixels from the left, right, top, and bottom, respectively.
    bits : int, optional, default 12
        Bit depth of the output image.
    dtype : numpy.dtype, optional, default numpy.float16
        Data type used for processing the data.

    Returns
    -------
    cor_data : numpy.ndarray
        Corrected data.
        
    """
    raw_data = BioImage(raw_img).data
    flat_data = BioImage(flat_img).data
    dark_data = BioImage(dark_img).data
    if len(roi) == 4:
        left, right, top, bottom = roi 
        flat_data = flat_data[..., top:bottom, left:right]
        dark_data = dark_data[..., top:bottom, left:right]
    med = np.median(flat_data - dark_data)
    try:
        import numexpr as ne
        cor_data = (ne.evaluate('(raw_data - dark_data) * med / (flat_data - dark_data)')).astype(dtype=dtype)
    except:
        cor_data = ((raw_data - dark_data) * med / (flat_data - dark_data)).astype(dtype=dtype)
    return cor_data
