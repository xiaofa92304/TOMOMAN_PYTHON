import sg_mrcread as sg_mrcread
import sg_mrcwrite as sg_mrcwrite
def tomoman_mrc_split(mrc_name, **kwargs):
    """
    A function to take in an mrc stack and write out the individual images.
    Optional inputs can be given as keyword arguments. Arguments are
    'outname' for the root name of the output stack and 'suffix' for adding
    an additional suffix to the root name. An optional 'digits' input is also
    available to set leading zeros. By default, the 'outname' is the same as
    the 'mrc_name', the 'suffix' is empty, and 'digits' is -1, which sets the
    leading zeros based on the number of tilts in the stack.
    
    Parameters:
    -----------
    mrc_name : str
        Path to the input MRC stack
    **kwargs : dict
        Optional keyword arguments:
        - outname: root name of the output stack
        - suffix: additional suffix to the root name
        - digits: number of leading zeros (-1 for auto)
        
    Returns:
    --------
    n_img : int
        Number of images in the stack
    """
    import os
    import math
    
    # Parse filename
    path, name = os.path.split(mrc_name)
    name, ext = os.path.splitext(name)
    
    if not path:
        path = '.'
    
    # Initialize options
    options = {
        'outname': os.path.join(path, name),
        'suffix': '',
        'digits': -1
    }
    
    # Update options with provided kwargs
    for key, value in kwargs.items():
        if key.lower() in options:
            options[key.lower()] = value
        else:
            raise ValueError(f"Achtung!!! Invalid parameter: {key}")
    
    # Check digits input
    if isinstance(options['digits'], str):
        options['digits'] = eval(options['digits'])
    
    if options['digits'] != int(options['digits']):
        raise ValueError("Achtung!!! Digits argument must be an integer!!!")
    elif options['digits'] < -1:
        raise ValueError("Achtung!!! Invalid digits argument. Number must be greater than -1!!!")
    
    # Read stack
    stack, header = sg_mrcread.sg_mrcread(mrc_name)
    n_img = stack.shape[2]
    
    # Autoset digits
    if options['digits'] == -1:
        options['digits'] = math.ceil(math.log10(n_img + 1))  # Should always work for integer counts
    
    # Split
    for i in range(1, n_img + 1):  # 1-based indexing to match MATLAB
        # String of image number
        num_str = f"{i:0{options['digits']}d}"
        
        # New filename
        new_name = f"{options['outname']}{options['suffix']}_{num_str}{ext}"
        
        # Write output - Python indexing is 0-based
        sg_mrcwrite.sg_mrcwrite(new_name, stack[:, :, i-1], header)
    
    print(f"{mrc_name} split!")
    
    return n_img