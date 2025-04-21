import os
import sys
import struct
import numpy as np
import sg_fread_mrcheader as sg_fread_mrcheader
def sg_read_mrc_header(mrc_name):
    """
    Read and return a .mrc header as a dictionary.
    
    Parameters:
    -----------
    mrc_name : str
        Path to the MRC file
        
    Returns:
    --------
    header : dict
        MRC header information
    """
    # Check computer type (endianness)
    if sys.byteorder == 'little':
        endian = '<'  # little-endian
    else:
        endian = '>'  # big-endian
    
    # Open file
    with open(mrc_name, 'rb') as fid:
        # Read header using helper function
        header = sg_fread_mrcheader.sg_fread_mrcheader(fid, endian)
    
    return header