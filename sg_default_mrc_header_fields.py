import numpy as np
def sg_default_mrc_header_fields():

    header_fields = [
        ('nx', 1),
        ('ny', 1),
        ('nz', 1),
        ('mode', 2),
        ('nxstart', 0),
        ('nystart', 0),
        ('nzstart', 0),
        ('mx', 1),
        ('my', 1),
        ('mz', 1),
        ('xlen', 1.0),
        ('ylen', 1.0),
        ('zlen', 1.0),
        ('alpha', 90.0),
        ('beta', 90.0),
        ('gamma', 90.0),
        ('mapc', 1),
        ('mapr', 2),
        ('maps', 3),
        ('amin', 0.0),
        ('amax', 0.0),
        ('amean', 0.0),
        ('ispg', 0),
        ('nsymbt', 0),
        ('next', 0),
        ('creatid', 0),
        ('nint', 0),
        ('nreal', 0),
        ('idtype', 0),
        ('lens', 0),
        ('nd1', 0),
        ('nd2', 0),
        ('vd1', 0),
        ('vd2', 0),
        ('tiltangles', np.zeros(6, dtype=np.float32)),
        ('xorg', 0.0),
        ('yorg', 0.0),
        ('zorg', 0.0),
        ('cmap', np.array([77, 65, 80, 32], dtype=np.int8)),  # "MAP "
        ('stamp', np.array([68, 65, 0, 0], dtype=np.int8)),   # "DA\0\0"
        ('rms', 0.0),
        ('nlabl', 0),
        ('labl', ['' for _ in range(10)])
    ]
    return header_fields