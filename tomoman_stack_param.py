def tomoman_stack_param(tomolist, st):
    """
    Update stack parameters in the tomolist.

    Parameters:
    tomolist (list): A list of dictionaries containing stack information.
    st (dict): A dictionary containing parameters.

    Returns:
    list: Updated tomolist with updated stack parameters.
    """

    tomolist['image_size'] = st['image_size']
    
    # Check if prealigned is not empty
    if 'prealigned' in st and st['prealigned']:
        tomolist['frames_aligned'] = True
        tomolist['frame_alignment_algorithm'] = st['prealigned']
        tomolist['stack_name'] = tomolist['raw_stack_name']

    return tomolist