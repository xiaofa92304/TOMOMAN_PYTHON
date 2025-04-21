def tomoman_gctf_parser(gctf_param):
    """
    A function to parse input arguments for gctf and generate a proper
    parameter string. If no arguments are given, either defaults are set or
    they are not added to the argument.
    
    Parameters:
    -----------
    gctf_param : dict
        Dictionary containing gctf parameters
        
    Returns:
    --------
    param_str : str
        Parameter string for gctf command
    """
    
    # Initialize fields
    # Format: [parameter_name, required/not_required, default_value]
    fields = [
        ['apix', 'req', ''],
        ['kV', 'req', '300'],
        ['cs', 'req', '2.7'],
        ['ac', 'req', '0.1'],
        ['phase_shift_L', 'nrq', '0.0'],
        ['phase_shift_H', 'nrq', '180.0'],
        ['phase_shift_S', 'nrq', '10.0'],
        ['phase_shift_T', 'nrq', '1'],
        ['dstep', 'nrq', '14.0'],
        ['defS', 'nrq', '500'],
        ['astm', 'nrq', '1000'],
        ['bfac', 'nrq', '150'],
        ['resL', 'nrq', '50'],
        ['resH', 'nrq', '4'],
        ['boxsize', 'nrq', '1024'],
        ['do_EPA', 'nrq', '0'],
        ['EPA_oversmp', 'nrq', '4'],
        ['overlap', 'nrq', '0.5'],
        ['convsize', 'nrq', '85'],
        ['do_Hres_ref', 'nrq', '0'],
        ['Href_resL', 'nrq', '15.0'],
        ['Href_resH', 'nrq', '4.0'],
        ['Href_bfac', 'nrq', '50'],
        ['B_resL', 'nrq', '15.0'],
        ['B_resH', 'nrq', '6.0'],
        ['do_mdef_refine', 'nrq', '0'],
        ['mdef_aveN', 'nrq', '1'],
        ['mdef_fit', 'nrq', '0'],
        ['mdef_ave_type', 'nrq', '0'],
        ['refine_input_ctf', 'nrq', '0'],
        ['input_ctfstar', 'nrq', 'none'],
        ['defU_init', 'nrq', '20000.0'],
        ['defV_init', 'nrq', '20000.0'],
        ['defA_init', 'nrq', '0.0'],
        ['B_init', 'nrq', '200.0'],
        ['defU_err', 'nrq', '500.0'],
        ['defV_err', 'nrq', '500.0'],
        ['defA_err', 'nrq', '15.0'],
        ['B_err', 'nrq', '50.0'],
        ['do_validation', 'nrq', '0'],
        ['ctfout_resL', 'nrq', '100.0'],
        ['ctfout_resH', 'nrq', ''],
        ['ctfout_bfac', 'nrq', '50'],
        ['input_ctfstar', 'nrq', 'micrographs_input_ctf.star'],
        ['boxsuffix', 'nrq', '_automatch.star'],
        ['ctfstar', 'nrq', 'micrographs_all_gctf.star'],
        ['logsuffix', 'nrq', '_gctf.log'],
        ['write_local_ctf', 'nrq', '0'],
        ['plot_res_ring', 'nrq', '1'],
        ['do_unfinished', 'nrq', ''],
        ['skip_check_mrc', 'nrq', ''],
        ['skip_check_gpu', 'nrq', ''],
        ['gid', 'nrq', '0']
    ]
    
    n_fields = len(fields)
    
    # Parse input
    # List to hold each argument
    parameters = [None] * n_fields
    
    for i in range(n_fields):
        # Check if field is empty or not written
        if fields[i][0] not in gctf_param:
            empty = True
        elif gctf_param[fields[i][0]] is None or gctf_param[fields[i][0]] == '':
            empty = True
        else:
            empty = False
        
        if empty and fields[i][1] == 'req':
            # If empty and required...
            if fields[i][2] != '':
                # Set parameter from default
                parameters[i] = f" --{fields[i][0]} {fields[i][2]}"
            else:
                raise ValueError(f"ACHTUNG!!! {fields[i][0]} is a required parameter!!!")
        
        elif not empty:
            # Convert value to string if it's numeric
            if isinstance(gctf_param[fields[i][0]], (int, float)):
                parameters[i] = f" --{fields[i][0]} {gctf_param[fields[i][0]]}"
            else:
                parameters[i] = f" --{fields[i][0]} {gctf_param[fields[i][0]]}"
    
    # Check for sets of options
    
    # Create a copy of parameters to modify
    filtered_parameters = parameters.copy()
    
    # Check for phase shift determination
    if not gctf_param.get('determine_pshift', False):
        # Remove phase shift parameters (indices 4-8)
        for i in range(4, 9):
            filtered_parameters[i] = None
    
    # Check for EPA
    if not gctf_param.get('do_EPA', False):
        # Remove EPA parameters (indices 16-19)
        for i in range(16, 20):
            filtered_parameters[i] = None
    
    # Check for high-res refinement
    if not gctf_param.get('do_Hres_ref', False):
        # Remove high-res refinement parameters (indices 20-23)
        for i in range(20, 24):
            filtered_parameters[i] = None
    
    # Check for movie defocus refinement
    if not gctf_param.get('do_mdef_refine', False):
        # Remove movie defocus refinement parameters (indices 26-29)
        for i in range(26, 30):
            filtered_parameters[i] = None
    
    # Check for refine input ctf
    if not gctf_param.get('refine_input_ctf', False):
        # Remove refine input ctf parameters (indices 30-39)
        for i in range(30, 40):
            filtered_parameters[i] = None
    
    # Generate parameter string by joining non-None parameters
    param_str = ''.join([p for p in filtered_parameters if p is not None])
    
    return param_str