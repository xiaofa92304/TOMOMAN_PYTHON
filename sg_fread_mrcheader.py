import sys
import struct
import numpy as np
def sg_fread_mrcheader(fid):
    """
    Read the header information of the opened MRC file.
    Parameter:
    fid: The opened file object
    Return:
    fid: File Object (Location updated)
    header: A dictionary containing header information

    """
    import numpy as np
    
    # Create a dictionary of header information
    header = {}
    
    # Dimension (column, row, slice)
    header['nx'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    header['ny'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    header['nz'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    
    header['mode'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    
    # The starting point of the sub-image (not used in IMOD)
    header['nxstart'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    header['nystart'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    header['nzstart'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    
    # The grid sizes in x,y, and z
    header['mx'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    header['my'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    header['mz'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    

    # Cell size in angstroms (pixel pitch = xlen/mx, ylen/my, zlen/mz)
    header['xlen'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    header['ylen'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    header['zlen'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    
    # Cell Angle (ignored in IMOD)
    header['alpha'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    header['beta'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    header['gamma'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    
    # Map columns, rows and slices. It must be set to 1,2,3 to obtain the correct pixel pitch.
    header['mapc'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    header['mapr'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    header['maps'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    
    # Data value information (must be set for appropriate scaling)
    header['amin'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    header['amax'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    header['amean'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    
    header['ispg'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    header['nsymbt'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    
    header['next'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    
    header['creatid'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    
    fid.seek(30, 1)
    
    header['nint'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    
    header['nreal'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    
    fid.seek(28, 1) 
    
    header['idtype'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    header['lens'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    header['nd1'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    header['nd2'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    header['vd1'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    header['vd2'] = np.fromfile(fid, dtype=np.int16, count=1)[0]
    
    header['tiltangles'] = np.fromfile(fid, dtype=np.float32, count=6)
    
    header['xorg'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    header['yorg'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    header['zorg'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    
    header['cmap'] = ''.join([chr(c) for c in np.fromfile(fid, dtype=np.int8, count=4)])
    
    header['stamp'] = np.fromfile(fid, dtype=np.int8, count=4)
    
    header['rms'] = np.fromfile(fid, dtype=np.float32, count=1)[0]
    
    header['nlabl'] = np.fromfile(fid, dtype=np.int32, count=1)[0]
    
    labl = np.fromfile(fid, dtype=np.int8, count=800)
    
    labl = labl.reshape((10, 80))
    header['labl'] = []
    
    for i in range(header['nlabl']):

        label_str = ''.join([chr(c) for c in labl[i] if c != 0]) 
        header['labl'].append(label_str)
    
    return fid, header