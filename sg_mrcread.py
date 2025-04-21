import numpy as np
import os
import struct
import sys
import sg_fread_mrcheader as fread
def sg_mrcread(mrc_name):
    """
    Read the MRC file and return the data and header information
    Parameter:
    mrc_name: The path of the MRC file
    Return:
    data: Array of image data
    header: Dictionary of header information

    """
    
    is_little_endian = (sys.byteorder == 'little')
    
    with open(mrc_name, 'rb') as fid:
        # Read the header information
        fid,header = fread.sg_fread_mrcheader(fid)
        
        fid.seek(1024 + header['next'], 0) 
        
        # reading data
        n_pixels = header['nx'] * header['ny'] * header['nz']
        
        if header['mode'] == 0:
            data = np.fromfile(fid, dtype=np.int8, count=n_pixels)
        elif header['mode'] == 1:
            data = np.fromfile(fid, dtype=np.int16, count=n_pixels)
        elif header['mode'] == 2:
            data = np.fromfile(fid, dtype=np.float32, count=n_pixels)
        
        # Reshape the data
        data = data.reshape((header['nx'], header['ny'], header['nz']))
        
    return data, header