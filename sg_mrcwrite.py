import numpy as np
import os
import sg_generate_mrc_header as generate
import sg_update_mrc_header as update
import sg_fwrite_mrcheader as fwrite
def sg_mrcwrite(mrc_name, data, header=None, **kwargs):


    if header is None:
        header = generate.sg_generate_mrc_header()
    
    try:
        fid = open(mrc_name, 'wb')
    except:
        raise IOError(f"ACHTUNG!!! Error opening file: {mrc_name}!!!")
    
    header = update.sg_update_mrc_header(data, header, **kwargs)
    
    fwrite.sg_fwrite_mrcheader(fid, header)
    
    data_flat = data.flatten()
    if header['mode'] == 0:
        fid.write(data_flat.astype(np.int8).tobytes())
    elif header['mode'] == 1:
        fid.write(data_flat.astype(np.int16).tobytes())
    elif header['mode'] == 2:
        fid.write(data_flat.astype(np.float32).tobytes())
    
    fid.close()