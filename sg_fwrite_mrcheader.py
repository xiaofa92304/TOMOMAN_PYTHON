import numpy as np
def sg_fwrite_mrcheader(fid, header):
    '''Write the MRC header information to the file'''
    # 解析标签
    label = np.zeros(800, dtype=np.int8)
    
    for i in range(header['nlabl']):
        s_idx = i * 80
        if len(header['labl'][i]) > 80:
            header['labl'][i] = header['labl'][i][:80]
        
        for j, char in enumerate(header['labl'][i]):
            label[s_idx + j] = ord(char)
    
    # Write header information
    fid.write(np.array(header['nx'], dtype=np.int32).tobytes())
    fid.write(np.array(header['ny'], dtype=np.int32).tobytes())
    fid.write(np.array(header['nz'], dtype=np.int32).tobytes())
    fid.write(np.array(header['mode'], dtype=np.int32).tobytes())
    fid.write(np.array(header['nxstart'], dtype=np.int32).tobytes())
    fid.write(np.array(header['nystart'], dtype=np.int32).tobytes())
    fid.write(np.array(header['nzstart'], dtype=np.int32).tobytes())
    fid.write(np.array(header['mx'], dtype=np.int32).tobytes())
    fid.write(np.array(header['my'], dtype=np.int32).tobytes())
    fid.write(np.array(header['mz'], dtype=np.int32).tobytes())
    fid.write(np.array(header['xlen'], dtype=np.float32).tobytes())
    fid.write(np.array(header['ylen'], dtype=np.float32).tobytes())
    fid.write(np.array(header['zlen'], dtype=np.float32).tobytes())
    fid.write(np.array(header['alpha'], dtype=np.float32).tobytes())
    fid.write(np.array(header['beta'], dtype=np.float32).tobytes())
    fid.write(np.array(header['gamma'], dtype=np.float32).tobytes())
    fid.write(np.array(header['mapc'], dtype=np.int32).tobytes())
    fid.write(np.array(header['mapr'], dtype=np.int32).tobytes())
    fid.write(np.array(header['maps'], dtype=np.int32).tobytes())
    fid.write(np.array(header['amin'], dtype=np.float32).tobytes())
    fid.write(np.array(header['amax'], dtype=np.float32).tobytes())
    fid.write(np.array(header['amean'], dtype=np.float32).tobytes())
    fid.write(np.array(header['ispg'], dtype=np.int16).tobytes())
    fid.write(np.array(header['nsymbt'], dtype=np.int16).tobytes())
    fid.write(np.array(header['next'], dtype=np.int32).tobytes())
    fid.write(np.array(header['creatid'], dtype=np.int16).tobytes())
    fid.write(np.zeros(30, dtype=np.int8).tobytes())  
    fid.write(np.array(header['nint'], dtype=np.int16).tobytes())
    fid.write(np.array(header['nreal'], dtype=np.int16).tobytes())
    fid.write(np.zeros(28, dtype=np.int8).tobytes())  
    fid.write(np.array(header['idtype'], dtype=np.int16).tobytes())
    fid.write(np.array(header['lens'], dtype=np.int16).tobytes())
    fid.write(np.array(header['nd1'], dtype=np.int16).tobytes())
    fid.write(np.array(header['nd2'], dtype=np.int16).tobytes())
    fid.write(np.array(header['vd1'], dtype=np.int16).tobytes())
    fid.write(np.array(header['vd2'], dtype=np.int16).tobytes())
    fid.write(np.array(header['tiltangles'], dtype=np.float32).tobytes())
    fid.write(np.array(header['xorg'], dtype=np.float32).tobytes())
    fid.write(np.array(header['yorg'], dtype=np.float32).tobytes())
    fid.write(np.array(header['zorg'], dtype=np.float32).tobytes())
    if isinstance(header['cmap'], str):
        fid.write(header['cmap'].encode('ascii'))
    else:
        fid.write(np.array(header['cmap'], dtype=np.int8).tobytes())
    fid.write(np.array(header['stamp'], dtype=np.int8).tobytes())
    fid.write(np.array(header['rms'], dtype=np.float32).tobytes())
    fid.write(np.array(header['nlabl'], dtype=np.int32).tobytes())
    fid.write(label.tobytes())
    
    return fid