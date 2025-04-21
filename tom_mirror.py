import numpy as np

def tom_mirror(img, dimsel, stmp=None):
    '''
    Realize the mirroring function of the MATLAB tom_mirror function
    param img: Input a three-dimensional numpy array (in the order of z,y,x)
    param dimsel: Mirror axis 'x', 'y' or 'z'
    param stmp: Optional splitting point
    return: The mirrored array
    '''

    if img.size == 0:
        return img
    
    # Select the processing method based on the dimension
    if dimsel == 'x':
        return mirror_x(img, stmp)
    elif dimsel == 'y':
        return mirror_y(img, stmp)
    elif dimsel == 'z':
        return mirror_z(img)
    else:
        raise ValueError("Unknown Dimension, must be 'x', 'y' or 'z'")

def mirror_x(img, stmp=None):
    
    s1, s2, s3 = img.shape
    c = np.zeros_like(img)
    
    stmp = s1 // 2 if stmp is None else stmp
    
    for i in range(s3):
        p1 = img[:stmp, :, i]
        p2 = img[stmp:, :, i]
        
        # Use symmetrical filling instead of padarray
        pad_width = ((0, stmp), (0, 0))
        p3 = np.pad(p1, pad_width, mode='symmetric')[:, :s1-stmp]
        p4 = np.pad(p2, ((stmp, 0), (0, 0)), mode='symmetric')[-stmp:]
        
        c[:, :, i] = np.vstack((p4, p3))
    
    return c

def mirror_y(img, stmp=None):
    s1, s2, s3 = img.shape
    c = np.zeros_like(img)
    
    stmp = s2 // 2 if stmp is None else stmp
    
    for i in range(s3):
        p1 = img[:, :stmp, i]
        p2 = img[:, stmp:, i]
        
        # Transpose the direction of the processing column
        pad_width = ((0, 0), (0, stmp))
        p3 = np.pad(p1.T, pad_width, mode='symmetric').T[:, stmp:]
        p4 = np.pad(p2.T, ((0, 0), (stmp, 0)), mode='symmetric').T[:, :stmp]
        
        c[:, :, i] = np.hstack((p4, p3))
    
    return c

def mirror_z(img):

    return img[::-1, :, :]