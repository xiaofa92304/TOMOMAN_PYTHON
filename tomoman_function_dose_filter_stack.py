import numpy as np
from numpy.fft import fft2, ifft2, ifftshift
import tomoman_frequencyarray as tomoman_frequencyarray

def tomoman_function_dose_filter_stack(input_stack, pixelsize, dose_list, a=None, b=None, c=None):
    """
    Exposure filter a tilt-stack using a modified version of the Grant and Grigorieff approach.
    
    This function applies exposure filters as low-pass filters without frequency reweighting.
    Therefore, reweighting should be performed after subtomogram averaging.
    
    Parameters:
    -----------
    input_stack : ndarray
        Input image stack (3D array)
    pixelsize : float
        Pixel size in Angstroms
    dose_list : list or ndarray
        List of doses in e/A^2 that matches the input stack
    a : float, optional
        Resolution-dependent critical exposure constant
    b : float, optional
        Resolution-dependent critical exposure constant
    c : float, optional
        Resolution-dependent critical exposure constant
        
    Returns:
    --------
    output_stack : ndarray
        Dose-filtered image stack
    """
    # Check parameters and set defaults if needed
    if a is None or b is None or c is None:
        # Hard-coded resolution-dependent critical exposures 
        a = 0.245
        b = -1.665
        c = 2.81
    print(a)
    print(b)
    print(c)
    # Get stack dimensions
    if input_stack.ndim == 3:
        z, x, y = input_stack.shape 
    else:
        x, y = input_stack.shape
        z = 1
        input_stack = input_stack.reshape(1, x, y)  

    # Check stack size
    if len(dose_list) != z:
        raise ValueError("ACHTUNG!!! Stack size and dose-list do not match!!!")
    
    # Initialize new stack
    output_stack = np.zeros((z, x, y), dtype=input_stack.dtype)
    
    # Initialize frequency array 
    freq_array = tomoman_frequencyarray.tomoman_frequencyarray(input_stack[0], pixelsize)
    epsilon = 1e-10 
    safe_freq_array = np.where(freq_array == 0, epsilon, freq_array)
    b = float(b)
    print(f"b type: {type(b)}, value: {b}")
    # Generate and apply filter for each tilt
    for i in range(z):
        # Calculate FFT 
        fft_img = fft2(input_stack[i].astype(float))
        
        # Calculate filter
        filter_values = ifftshift(np.exp((-dose_list[i]) / (2 * ((a * (safe_freq_array ** b)) + c))))
        
        # Calculate new image
        output_stack[i] = np.real(ifft2(fft_img * filter_values))
        
        print(f"TOMOMAN: Image {i+1} of {z} filtered...")
    
    # If input was 2D, return 2D output 
    if z == 1:
        output_stack = output_stack[0]
        
    return output_stack