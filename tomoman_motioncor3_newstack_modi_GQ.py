import os
import numpy as np
from scipy.io import savemat, loadmat
from skimage.transform import resize
import tomoman_motioncor3_batch_wrapper_modi_GQ as wrapper
import sg_mrcread as mrcread
import tom_mirror as mirror
import sg_generate_mrc_header as sg_generate_mrc_header
import sg_append_mrc_label_enhanced as sg_append_mrc_label_enhanced
import sg_mrcwrite as mrcwrite
import dlmwrite as dlmwrite
import tomoman_resize_stack as resize_stack
def tomoman_motioncor3_newstack_modi_GQ(tomolist, p, a, mc3, write_list):
    """
    A function for looping through a tomolist and running MotionCor3 on the
    frames and generating a new, properly ordered, stack.

    Parameters:
    tomolist (list): A list of dictionaries containing stack information.
    p (dict): A dictionary containing parameters.
    a (dict): A dictionary containing parameters.
    mc3 (dict): A dictionary containing parameters.
    write_list (bool): Whether to save the updated tomolist.

    Returns:
    list: Updated tomolist with updated stack parameters.
    """
    
    process = False
    
    # Check for skip
    if not tomolist['skip']:
        process = True
    
    # Check for previous alignment
    if process and not tomolist['frames_aligned']:
        process = True
    else:
        process = False
    
    # Check for force_realign
    if mc3['force_realign'] and not tomolist['skip']:
        process = True
    
    # Process stack
    if process:
        # Parse tomogram string
        tomo_str = f'{tomolist["tomo_num"]:0{p["digits"]}}'
        
        # Number of tilts
        n_tilts = len(tomolist['collected_tilts'])
        
        # Generate stack order
        sorted_tilts = np.sort(tomolist['collected_tilts'])
        unsorted_idx = np.argsort(tomolist['collected_tilts'])
        
        # Generate temporary output names
        mc3_dir = os.path.join(tomolist['stack_dir'], 'MotionCor3/')
        if not os.path.exists(mc3_dir):
            os.makedirs(mc3_dir)
        ali_names = [os.path.join(mc3_dir, f'{tomo_str}_{unsorted_idx[j]}.mrc') for j in range(n_tilts)]

        # Generate input names
        input_names = [
            os.path.join(tomolist["frame_dir"], filename)  
            for filename in tomolist["frame_names"][:n_tilts]  
        ]
        
        # Run motioncor3
        print(f'Running MotionCor3 on stack {tomo_str}')
        wrapper.tomoman_motioncor3_batch_wrapper_modi_GQ(input_names, ali_names, tomolist, mc3)
        
        # Assemble new stack
        print(f'MotionCor3 complete on stack {tomo_str}... Generating new stack!!!')
        
        # New stack parameters
        if a['stack_prefix']:
            stack_names = [f'{p["prefix"]}{tomo_str}.st']
        else:
            stack_names = [f'{tomo_str}.st']
        stack_types = ['normal']
        num_stacks = 1
        
        # Additional stack parameters for dose filtering
        if mc3['dose_filter']:
            stack_names.append(f'{tomo_str}_dose_filt.st')
            stack_types.append('dose_filt')
            num_stacks = 2
        
        # Generate stacks
        new_stack = {}
        for j in range(num_stacks):
                        
            for k in range(n_tilts):
                
                img = mrcread.sg_mrcread(f"{mc3_dir}{tomo_str}_{k}.mrc")
                
      
                if k == 0:
 
                    new_stack[stack_types[j]] = np.zeros((a['image_size'][0], a['image_size'][1], n_tilts), dtype=img[0].dtype)
                
        
                img = resize_stack.tomoman_resize_stack(img[0], a['image_size'][0], a['image_size'][1], True)
                if tomolist['mirror_stack'] != 'n' or not tomolist['mirror_stack']:
                    img = mirror.tom_mirror(img, tomolist['mirror_stack'])
                    
                new_stack[stack_types[j]][:,:,k] = np.squeeze(img) 
        
            # Write outputs
            header = sg_generate_mrc_header.sg_generate_mrc_header()
            header = sg_append_mrc_label_enhanced.sg_append_mrc_label(header, 'TOMOMAN: Frames aligned with MotionCor3.')
            for j in range(num_stacks):
                mrcwrite.sg_mrcwrite(os.path.join(tomolist['stack_dir'], stack_names[j]), new_stack[stack_types[j]], header, pixelsize=tomolist['pixelsize'])
                stname = os.path.splitext(os.path.basename(stack_names[j]))[0]
                dlmwrite.dlmwrite(os.path.join(tomolist['stack_dir'], stname + '.rawtlt'), sorted_tilts)
            
        # Update tomolist
        tomolist['image_size'] = a['image_size']
        tomolist['frames_aligned'] = True
        tomolist['frame_alignment_algorithm'] = 'MotionCor3'
        tomolist['stack_name'] = stack_names[0]
        if mc3['dose_filter']:
            tomolist['dose_filtered'] = True
            tomolist['dose_filtered_stack_name'] = stack_names  [1]
            tomolist['dose_filter_algorithm'] = 'MotionCor3'
        
        # Save tomolist
        if write_list:
            savemat(os.path.join(p['root_dir'], p['tomolist_name']), {'tomolist': tomolist})
        
        # Clean temporary files
        for j in range(n_tilts):
            os.remove(ali_names[j])
        if mc3['dose_filter']:
            for j in range(n_tilts):
                path, name, _ = os.path.splitext(ali_names[j])
                os.remove(f'{path}/{name}_DW.mrc')
    
    return tomolist