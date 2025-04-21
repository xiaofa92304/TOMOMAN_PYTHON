import os
import numpy as np
from scipy.io import savemat
import mrcfile
import tomoman_function_dose_filter_stack as tomoman_function_dose_filter_stack
import tomoman_function_dose_filter_frame_stack as tomoman_function_dose_filter_frame_stack
import tomoman_resize_stack as tomoman_resize_stack
import tom_mirror as tom_mirror
import sg_read_mrc_header as sg_read_mrc_header
import sg_generate_mrc_header as sg_generate_mrc_header

def tomoman_exposure_filter(tomolist, p, st, df, write_list):
    """
    Take a tomolist and exposure filter stacks using the Grant and Grigorieff exposure filters.
    
    Parameters:
    -----------
    tomolist : dict
        Dictionary of tomogram information
    p : dict
        Parameters dictionary
    st : dict
        Stack parameters
    df : dict
        Dose filter parameters
    write_list : bool
        Whether to write the updated tomolist to disk
        
    Returns:
    --------
    tomolist : dict
        Updated tomolist with dose filtering information
    """
    # Check parameters and set defaults if needed
    if 'a' not in df or 'b' not in df or 'c' not in df or df['a'] is None or df['b'] is None or df['c'] is None:
        # Hard-coded resolution-dependent critical exposures 
        a = 0.245
        b = -1.665
        c = 2.81
    else:
        a = df['a']
        b = df['b']
        c = df['c']
    
    if not tomolist['skip']:
        process = True
    else:
        process = False
        
    # Check for previous alignment
    if process and not tomolist['dose_filtered']:
        process = True
    else:
        process = False
        
    # Check for force_realign
    if df['force_dfilt'] and not tomolist['skip']:
        process = True
    
    if process:
        print(f"TOMOMAN: Dose filtering stack: {tomolist['stack_name']}")
        
        # Find tilts
        collected_tilts = np.array(tomolist['collected_tilts'])
        removed_tilts = np.array(tomolist['removed_tilts'])
        
        # Find tilts that are in collected_tilts but not in removed_tilts
        mask = np.isin(collected_tilts, removed_tilts, invert=True)
        tilts = collected_tilts[mask]
        tilt_idx = np.where(mask)[0]
        
        # Sort tilts according to tilt_order
        if st['tilt_order'] == 'ascend':
            sort_idx = np.argsort(tilts)
        else:  # 'descend'
            sort_idx = np.argsort(-tilts)
            
        tilts = tilts[sort_idx]
        tilt_idx = tilt_idx[sort_idx]
        n_tilts = len(tilts)
        
        # Parse doses and order with respect to stack
        dose_array = np.zeros((n_tilts, 2))
        dose_array[:, 0] = tilts
        dose_array[:, 1] = [tomolist['dose'][idx] + df['preexposure'] for idx in tilt_idx]
        
        # Parse stack names
        st_name, st_ext = os.path.splitext(tomolist['stack_name'])
        newstack_name = f"{st_name}{df['dfilt_append']}{st_ext}"
        
        # Apply exposure filters
        if not df['filter_frames']:  # Case 0: Apply filter to stack
            print("TOMOMAN: Exposure filtering image stack...")
            
            # Read stack
            print(f"TOMOMAN: Reading stack {tomolist['stack_name']}...")
            stack_path = os.path.join(tomolist['stack_dir'], tomolist['stack_name'])
            with mrcfile.open(stack_path) as mrc:
                stack = mrc.data
                header = mrc.header
            
            # Exposure filter
            df_stack = tomoman_function_dose_filter_stack.tomoman_function_dose_filter_stack(stack, tomolist['pixelsize'], dose_array[:, 1], a, b, c)
            
            # Header label
            dose_str = f"{tomolist['dose'][0]/tomolist['cumulative_exposure_time'][0]:.4f}"
            label = f"TOMOMAN: Exposure filtered on images with {dose_str} e/(A^2)/s"
            
            # Update tomolist
            tomolist['dose_filter_algorithm'] = 'TOMOMAN-images'
            
        else:  # Case 1: Exposure filtering frame stacks
            print("TOMOMAN: Exposure filtering frame stacks...")
            
            # Initialize stack
            df_stack = np.zeros((tomolist['image_size'][0], tomolist['image_size'][1], n_tilts))
            
            # Loop through frame stacks
            for j in range(n_tilts):
                # Generate stack order
                sorted_idx = np.argsort(tomolist['collected_tilts'])
                frame_idx = np.where(sorted_idx == tilt_idx[j])[0][0] + 1  # +1 to match MATLAB 1-based indexing
                
                # Frame stack name
                tomo_str = f"{tomolist['tomo_num']:0{p['digits']}d}"
                frame_name = f"{tomo_str}_{frame_idx}_Stk.mrc"
                
                # Final dose
                final_dose = dose_array[j, 1]
                
                # Initial dose
                if tilt_idx[j] == 0:  # First tilt
                    init_dose = df['preexposure']
                else:
                    init_dose = tomolist['dose'][tilt_idx[j]-1] + df['preexposure']
                
                # Calculate dose per frame
                if len(tomolist['n_frames']) == 1:
                    dpf = (final_dose - init_dose) / tomolist['n_frames']
                else:
                    dpf = (final_dose - init_dose) / tomolist['n_frames'][j]
                
                # Read frame stack
                print(f"TOMOMAN: Reading stack {frame_name}...")
                try:
                    frame_path = os.path.join(tomolist['stack_dir'], "MotionCor2", frame_name)
                    with mrcfile.open(frame_path) as mrc:
                        frame_stack = mrc.data
                except Exception as e:
                    raise Exception(f"ACHTUNG!!! Frame stack {frame_path} not found!!! Did you remember to generate aligned frame stacks with MotionCor2??? Error: {str(e)}")
                
                # Filter stack
                filt_img = tomoman_function_dose_filter_frame_stack.tomoman_function_dose_filter_frame_stack(frame_stack, tomolist['pixelsize'], init_dose, dpf, a, b, c)
                filt_img = tomoman_resize_stack.tomoman_resize_stack(filt_img, tomolist['image_size'][0], tomolist['image_size'][1], True)
                
                if tomolist['mirror_stack'] != 'none':
                    filt_img = tom_mirror.tom_mirror(filt_img, tomolist['mirror_stack'])
                
                df_stack[:, :, j] = filt_img
            
            # Grab header from stack
            try:
                header = sg_read_mrc_header(os.path.join(tomolist['stack_dir'], tomolist['stack_name']))
            except:
                header = sg_generate_mrc_header.sg_generate_mrc_header()
            
            # Header label
            dose_str = f"{tomolist['dose'][0]/tomolist['cumulative_exposure_time'][0]:.4f}"
            label = f"TOMOMAN: Exposure filtered on frames with {dose_str} e/(A^2)/s"
            
            # Update tomolist
            tomolist['dose_filter_algorithm'] = 'TOMOMAN-frames'
        
        # Write stack with header
        print(f"TOMOMAN: Saving dose filtered stack {newstack_name}!!!")
        output_path = os.path.join(tomolist['stack_dir'], newstack_name)
        with mrcfile.new(output_path, overwrite=True) as mrc:
            mrc.set_data(df_stack.astype(np.float32))
            # Copy header values and set pixel size
            # Note: mrcfile handles headers differently than MATLAB
            mrc.voxel_size = (tomolist['pixelsize'], tomolist['pixelsize'], tomolist['pixelsize'])
            # Add label
            mrc.header.label[0] = label.encode()
        
        # Update tomolist
        tomolist['dose_filtered'] = True
        tomolist['dose_filtered_stack_name'] = newstack_name
        
        # Write rawtilt file
        rawtilt_path = os.path.join(tomolist['stack_dir'], f"{st_name}{df['dfilt_append']}.rawtlt")
        np.savetxt(rawtilt_path, tomolist['rawtlt'], fmt='%.6f')
        
        # Save tomolist
        if write_list:
            tomolist_path = os.path.join(p['root_dir'], p['tomolist_name'])
            savemat(tomolist_path, {'tomolist': tomolist})

    return tomolist