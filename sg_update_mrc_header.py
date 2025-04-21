import sg_default_mrc_header_fields as default
import numpy as np
def sg_update_mrc_header(data, header=None, **kwargs):
    
    # Initialize the default header field
    header_fields = default.sg_default_mrc_header_fields()
    
    # Check the input header information
    if header is None:
        header = default.sg_generate_mrc_header(header_fields)
    
    # Non-header information input
    non_header = ['pixelsize']
    
    # Parse pixel size
    if 'pixelsize' in kwargs:
        pixelsize_value = kwargs['pixelsize']
        if isinstance(pixelsize_value, (int, float)):
            pixelsize = [pixelsize_value] * 3
        elif len(pixelsize_value) == 2:
            pixelsize = [pixelsize_value[0], pixelsize_value[1], 1]
        elif len(pixelsize_value) == 3:
            pixelsize = pixelsize_value
        else:
            raise ValueError("ACHTUNG!!! Pixel size must be given with either 1, 2, or 3 dimensions!!!")
    else:
        # Try to parse the pixel size from the old header information
        pixelsize = [
            header['xlen'] / float(header['mx']),
            header['ylen'] / float(header['my']),
            header['zlen'] / float(header['mz'])
        ]
        for i in range(3):
            if np.isnan(pixelsize[i]):
                pixelsize[i] = 1
    
    # Update the header information from the input parameters
    for key, value in kwargs.items():
        if key not in [field[0] for field in header_fields] and key not in non_header:
            raise ValueError(f"ACHTUNG!!! Invalid input argument: {key}!!!")
        if key in header:
            header[key] = value
    
    # Update the fields related to the data
    
    if data.ndim == 1:
        x, y, z = data.shape[0], 1, 1
    elif data.ndim == 2:
        x, y, z = data.shape[0], data.shape[1], 1
    else:
        x, y, z = data.shape
    
    header['nx'] = x
    header['ny'] = y
    header['nz'] = z
    header['mx'] = x
    header['my'] = y
    header['mz'] = z
    
    header['xlen'] = x * pixelsize[0]
    header['ylen'] = y * pixelsize[1]
    header['zlen'] = z * pixelsize[2]
    
    header['amin'] = float(np.min(data))
    header['amax'] = float(np.max(data))
    header['amean'] = float(np.mean(data))
    
    if data.dtype == np.int8:
        header['mode'] = 0
    elif data.dtype == np.int16:
        header['mode'] = 1
    elif data.dtype in [np.float32, np.float64]:
        header['mode'] = 2
    else:
        raise ValueError("ACHTUNG!!! Input data has unsupported data type!!! Only 'int8', 'int16', and 'float' supported!!!")
    
    return header