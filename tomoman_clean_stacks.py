import os
import numpy as np
import subprocess

def tomoman_clean_stacks(tomolist, p, c, st, write_list=True, root_dir=None, tomolist_name=None, skip_3dmod=False):
    """
    A function for launching a tilt-stack in 3dmod, and waiting for input
    tilts to remove. Tilts are then removed, and rawtlt files are updated.
    
    By running this command, the remove tilts are appended to the
    removed_tilts field of the tomolist, while the stack_name is updated to
    the cleaned stack. The tilts of the stack denoted by stack_name is the
    set difference between collected_tilts and removed_tilts. Therefore, this
    command can be run serially to re-clean stacks.
    
    If dose-filtered stacks have already been generated, those stacks are
    also cleaned to match the unfiltered stacks.
    
    Parameters:
    -----------
    tomolist : list of dict
        List of tomogram dictionaries containing metadata
    p : dict
        Parameters dictionary
    c : dict
        Configuration dictionary
    st : dict
        Stack parameters dictionary
    write_list : bool, optional
        Whether to save the updated tomolist
    root_dir : str, optional
        Root directory for saving tomolist
    tomolist_name : str, optional
        Name of the tomolist file to save
    skip_3dmod : bool, optional
        Whether to skip launching 3dmod and directly input tilt numbers to remove
        
    Returns:
    --------
    tomolist : list of dict
        Updated tomolist with cleaned stacks
    """

    # Check for skip
    if not tomolist['skip']:
        process = True
    else:
        process = False
        
    # Check for previous alignment
    if process and not tomolist['clean_stack']:
        process = True
    else:
        process = False
        
    # Check for force_cleaning
    if bool(c['force_cleaning']) and not tomolist['skip']:
        process = True

    # Process stack
    if process:
        
        # Parse tomogram string
        tomo_str = f"{tomolist['tomo_num']:0{p['digits']}d}"
        
        # Determine tilts in stack
        collected_tilts = np.array(tomolist['collected_tilts'])
        removed_tilts = np.array(tomolist['removed_tilts'])
        
        # Sort tilts according to tilt_order (ascending or descending)
        tilts = np.setdiff1d(collected_tilts, removed_tilts)
        if st['tilt_order'] == 'descend':
            tilts = np.sort(tilts)[::-1]
        else:
            tilts = np.sort(tilts)
    
        # Launch tilt-stack in 3dmod if not skipping
        if not skip_3dmod:
            cmd = f"3dmod -b {c['clean_binning']} {tomolist['stack_dir']}{tomolist['stack_name']}"
            subprocess.run(cmd, shell=True)
        else:
            # If skipping 3dmod, print available tilts for reference
            print(f"\nStack {tomo_str} - Available tilts:")
            for idx, tilt in enumerate(tilts, 1):
                print(f"{idx}: {tilt}")
        
        # Ask for input about bad tilts
        wait = False
        while not wait:
            # Wait for user input
            print('\nPress enter for no cleaning, give tilt numbers to remove (space separated), or skip, to prevent further processing of stack')
            assess_string = input('Which tilts should I remove? (Start counting at one) \n')
            
            # Empty string is no bad tilts, skip sets the skip value in the tomolist
            if not assess_string or assess_string == 'skip':
                wait = True
            else:
                # Check input is only numbers and whitespace
                if all(c.isdigit() or c.isspace() for c in assess_string):
                    bad_tilts = [int(x) for x in assess_string.split()]
                    wait = True
                else:
                    print('Your input is unacceptable!!!')
        
        # If there are bad tilts, fix the stack
        if assess_string == 'skip':
            
            # Set tomolist to skip
            tomolist['skip'] = True
            print(f"Stack {tomo_str} set to skip!!!")
            
        else:
            
            # Parse stack name
            stack_path = tomolist['stack_name']
            st_name, st_ext = os.path.splitext(os.path.basename(stack_path))
            
            if not assess_string:
                print('No bad tilts... moving on to next stack!!!')
                
                if tomolist['dose_filtered_stack_name'] != 'none':
                    df_st_name = os.path.splitext(os.path.basename(tomolist['dose_filtered_stack_name']))[0]
            
            else:
                print(f"Removing bad tilts in stack {tomo_str}")
                
                # Parse exclusion array into string (subtract 1 for 0-based indexing)
                exclude_list = ','.join([str(x-1) for x in bad_tilts])
                
                # Write out cleaned frame stack using newstack
                newstack_name = f"{st_name}{c['clean_append']}{st_ext}"
                cmd = (f"newstack -input {tomolist['stack_dir']}{tomolist['stack_name']} "
                        f"-output {tomolist['stack_dir']}{newstack_name} "
                        f"-exclude {exclude_list}")
                subprocess.run(cmd, shell=True)
                tomolist['stack_name'] = newstack_name
                
                # Check for dose-filtered stack
                if tomolist['dose_filtered_stack_name'] != 'none':
                    df_stack_path = tomolist['dose_filtered_stack_name']
                    df_st_name, df_st_ext = os.path.splitext(os.path.basename(df_stack_path))
                    df_newstack_name = f"{df_st_name}{c['clean_append']}{df_st_ext}"
                    
                    cmd = (f"newstack -input {tomolist['stack_dir']}{tomolist['dose_filtered_stack_name']} "
                            f"-output {tomolist['stack_dir']}{df_newstack_name} "
                            f"-exclude {exclude_list}")
                    subprocess.run(cmd, shell=True)
                    tomolist['dose_filtered_stack_name'] = df_newstack_name
                
                # Append removed_tilts
                bad_angles = tilts[np.array(bad_tilts) - 1]  # Convert to 0-based indexing
                
                # Combine existing and new removed tilts
                combined_removed = np.append(tomolist['removed_tilts'], bad_angles)
                
                # Sort according to tilt_order
                if st['tilt_order'] == 'descend':
                    tomolist['removed_tilts'] = sorted(combined_removed, reverse=True)
                else:
                    tomolist['removed_tilts'] = sorted(combined_removed)
                
                # Recalculate remaining tilts
                tilts = np.setdiff1d(collected_tilts, tomolist['removed_tilts'])
                if st['tilt_order'] == 'descend':
                    tilts = np.sort(tilts)[::-1]
                else:
                    tilts = np.sort(tilts)
            
            # Update remaining tomolist parameters
            tomolist['clean_stack'] = True
            tomolist['rawtlt'] = tilts.tolist()
            tomolist['min_tilt'] = float(min(tilts))
            tomolist['max_tilt'] = float(max(tilts))
            
            # Write rawtilt file
            rawtlt_path = f"{tomolist['stack_dir']}{st_name}{c['clean_append']}.rawtlt"
            np.savetxt(rawtlt_path, tomolist['rawtlt'], fmt='%.6f')
            
            if tomolist['dose_filtered_stack_name'] != 'none':
                df_rawtlt_path = f"{tomolist['stack_dir']}{df_st_name}{c['clean_append']}.rawtlt"
                np.savetxt(df_rawtlt_path, tomolist['rawtlt'], fmt='%.6f')
        
        # Save tomolist
        if write_list and root_dir is not None and tomolist_name is not None:
            import pickle
            with open(os.path.join(root_dir, tomolist_name), 'wb') as f:
                pickle.dump(tomolist, f)
    
    return tomolist