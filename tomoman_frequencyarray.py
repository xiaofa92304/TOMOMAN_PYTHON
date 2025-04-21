import numpy as np

def tomoman_frequencyarray(image, pixelsize):
    """
    Generate an array with Fourier space frequencies from a volume and pixelsize.
    
    Parameters:
    -----------
    image : ndarray
        Input image/volume
    pixelsize : float
        Pixel size in Angstroms
        
    Returns:
    --------
    f_array : ndarray
        Array with Fourier space frequencies
    """
    # Get size of image
    if image.ndim == 2:
        dimx, dimy = image.shape
        dimz = 1
    else:
        dimx, dimy, dimz = image.shape
    
    # Create coordinate grids
    if dimz == 1:
        # 2D case
        x = np.arange(-np.floor(dimx/2), -np.floor(dimx/2) + dimx)
        y = np.arange(-np.floor(dimy/2), -np.floor(dimy/2) + dimy)
        
        # Create meshgrid (equivalent to MATLAB's ndgrid)
        x, y = np.meshgrid(x, y, indexing='ij')
        
        # Projected reciprocal distance array
        rx = x / (dimx * pixelsize)
        ry = y / (dimy * pixelsize)
        
        # Calculate frequency array
        f_array = np.sqrt(rx**2 + ry**2)
    else:
        # 3D case
        x = np.arange(-np.floor(dimx/2), -np.floor(dimx/2) + dimx)
        y = np.arange(-np.floor(dimy/2), -np.floor(dimy/2) + dimy)
        z = np.arange(-np.floor(dimz/2), -np.floor(dimz/2) + dimz)
        
        # Create meshgrid (equivalent to MATLAB's ndgrid)
        x, y, z = np.meshgrid(x, y, z, indexing='ij')
        
        # Projected reciprocal distance array
        rx = x / (dimx * pixelsize)
        ry = y / (dimy * pixelsize)
        rz = z / (dimz * pixelsize)
        
        # Calculate frequency array
        f_array = np.sqrt(rx**2 + ry**2 + rz**2)
    
    return f_array