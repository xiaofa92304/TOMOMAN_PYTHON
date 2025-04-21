import numpy as np
from numpy.fft import fft2, ifft2, ifftshift
import tomoman_frequencyarray as tomoman_frequencyarray
def tomoman_function_dose_filter_frame_stack(input_stack, pixelsize, initial_dose, dose_per_frame, a=None, b=None, c=None):
    """
    Exposure filter a frame stack using a modified version of the Grant and Grigorieff approach.
    
    This function applies exposure filters that are reweighted by the inverse of the
    sum of the squares, multiplied by the first filter. This is because the
    high-resolution information content of the summed image should not be
    higher than the exposure filter, otherwise noise is amplified.
    
    Parameters:
    -----------
    input_stack : ndarray
        Input image stack (3D array)
    pixelsize : float
        Pixel size in Angstroms
    initial_dose : float
        Initial dose prior to imaging in e/A^2
    dose_per_frame : float
        Dose per frame in e/A^2
    a : float, optional
        Resolution-dependent critical exposure constant
    b : float, optional
        Resolution-dependent critical exposure constant
    c : float, optional
        Resolution-dependent critical exposure constant
        
    Returns:
    --------
    filt_img : ndarray
        Dose-filtered and reweighted image
    """
    # Check parameters and set defaults if needed
    if a is None or b is None or c is None:
        # Hard-coded resolution-dependent critical exposures 
        a = 0.245
        b = -1.665
        c = 2.81
    
    # Get stack dimensions
    x, y, z = input_stack.shape
    
    # Initialize filter stack
    filter_stack = np.zeros((x, y, z))
    
    # Filtered image
    fft_sum = np.zeros((x, y), dtype=complex)
    
    # Initialize frequency array
    freq_array = tomoman_frequencyarray.tomoman_frequencyarray(input_stack[:, :, 0], pixelsize)
    
    # Generate and apply filter for each frame
    for i in range(z):
        # Calculate FFT
        fft_img = fft2(input_stack[:, :, i].astype(float))
        
        # Calculate dose
        dose = initial_dose + (dose_per_frame * (i + 1))
        
        # Calculate filter
        filter_stack[:, :, i] = ifftshift(np.exp(-dose / (2 * ((a * (freq_array ** b)) + c))))
        
        # Calculate new image
        fft_sum = fft_sum + (fft_img * filter_stack[:, :, i])
        
        print(f"TOMOMAN: Frame {i+1} of {z} filtered...")
    
    # Reweighting filter
    reweight_filter = filter_stack[:, :, 0] / np.sqrt(np.sum(filter_stack**2, axis=2) / z)
    
    # Filtered image
    filt_img = np.real(ifft2(fft_sum * reweight_filter))
    
    return filt_img