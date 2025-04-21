import os
import numpy as np
import math
import subprocess
import shutil
import tomoman_gctf_star_to_ctfphaseflip as tomoman_gctf_star_to_ctfphaseflip
import tomoman_mrc_split as tomoman_mrc_split
import sg_mrcread as sg_mrcread
import sg_mrcwrite as sg_mrcwrite
import tomoman_gctf_parser as tomoman_gctf_parser
def tomoman_gctf(tomolist, p, gctf_param, write_list):
    """
    A function for taking a tomolist and running GCTF. GCTF is run by first
    splitting the non-dose-filtered stack, running GCTF, and concatenating the
    results. The results are also converted into IMOD/ctfphaseflip format.
    
    Parameters:
    -----------
    tomolist : list
        List of tomogram information dictionaries
    p : dict
        Processing parameters
    gctf_param : dict
        GCTF parameters
    write_list : bool
        Whether to write the updated tomolist to disk
        
    Returns:
    --------
    tomolist : list
        Updated list of tomogram information dictionaries
    """
    
    # Run GCTF
    n_stacks = len(tomolist)
    
    for i in range(n_stacks):
        
        # Check for skip
        if not tomolist['skip']:
            process = True
        else:
            process = False
            
        # Check for previous alignment
        if process and not tomolist['ctf_determined']:
            process = True
        else:
            process = False
            
        # Check for force_realign
        if bool(gctf_param['force_gctf']) and not tomolist['skip']:
            process = True
        
        if process:
            print(f"TOMOMAN: Determining defocus of stack {tomolist['stack_name']} with GCTF!!!")
            
            # Parse stack name
            stack_dir, stack_filename = os.path.split(tomolist['stack_name'])
            st_name, st_ext = os.path.splitext(stack_filename)
            
            # Make GCTF folder
            gctf_dir = os.path.join(tomolist['stack_dir'], 'gctf')
            temp_dir = os.path.join(gctf_dir, 'temp')
            
            if not os.path.exists(gctf_dir):
                os.makedirs(gctf_dir)
                os.makedirs(temp_dir)
            elif not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
            
            # Parse parameters
            gctf_param['apix'] = tomolist['pixelsize']
            param_str = tomoman_gctf_parser.tomoman_gctf_parser(gctf_param)
            
            # Defocus options
            defL = (tomolist['target_defocus'] * -10000) - gctf_param['defWidth']
            defH = (tomolist['target_defocus'] * -10000) + gctf_param['defWidth']
            def_param = f" --defL {defL} --defH {defH}"
            print(tomolist['rawtlt'])
            # Number of images
            n_img = len(tomolist['rawtlt'])
            # Digits for leading zeros
            digits = math.ceil(math.log10(n_img + 1))
            
            # Prepare inputs for GCTF
            if gctf_param['input_type'] == 'stack':
                
                # Split stack
                print("TOMOMAN: Splitting stack!!!")
                stack_path = os.path.join(tomolist['stack_dir'], tomolist['stack_name'])
                outname = os.path.join(tomolist['stack_dir'], 'gctf', 'temp', st_name)
                temp_n_img = tomoman_mrc_split.tomoman_mrc_split(stack_path, outname=outname, digits=-1)
                print(temp_n_img)
                print(n_img)
                if n_img != temp_n_img:
                    raise ValueError(f"ACHTUNG!!! Number of tilts in stack \"{tomolist['stack_name']}\" do not match the tomolist rawtlt!!!")
                
            elif gctf_param['input_type'] == 'frames':
                print("TOMOMAN: Preparing frames!!!")
                
                # Find frames in stack
                frame_idx = []
                for tilt in tomolist['rawtlt']:
                    if tilt in tomolist['collected_tilts']:
                        frame_idx.append(tomolist['collected_tilts'].index(tilt))
                
                # Convert frames to .mrc files
                for j in range(n_img):
                    
                    # Check if tiff
                    _, frame_ext = os.path.splitext(tomolist['frame_names'][frame_idx[j]])
                    if frame_ext.lower() in ['.tif', '.tiff']:
                        
                        # Options for conversion
                        clip_opt1 = ""
                        clip_opt2 = ""
                        clip_opt3 = ""
                        
                        # Check for defects
                        if tomolist['defects_file']:
                            clip_opt1 = f" -D {tomolist['defects_file']}"
                        
                        # Check for gainref
                        if tomolist['defects_file']:
                            clip_opt2 = f" -R {tomolist['rotate_gain']}"
                            clip_opt3 = f" {tomolist['gainref']}"
                        
                        frame_path = os.path.join(tomolist['frame_dir'], tomolist['frame_names'][frame_idx[j]])
                        output_path = os.path.join(tomolist['stack_dir'], 'gctf', 'temp', f"{st_name}_{j:0{digits}d}.st")
                        
                        cmd = f"clip unpack{clip_opt1}{clip_opt2} {frame_path}{clip_opt3} {output_path}"
                        subprocess.run(cmd, shell=True)
            
            # Run GCTF
            cmd = f"gctf {def_param}{param_str} {os.path.join(tomolist['stack_dir'], 'gctf', 'temp', st_name)}_*"
            subprocess.run(cmd, shell=True)
            
            # Copy .star file
            shutil.move('./micrographs_all_gctf.star', os.path.join(tomolist['stack_dir'], 'gctf'))
            
            # Concatenate log files
            cmd = f"cat {os.path.join(tomolist['stack_dir'], 'gctf', 'temp')}/*_gctf.log > {os.path.join(tomolist['stack_dir'], 'gctf', st_name)}_gctf.log"
            subprocess.run(cmd, shell=True)
            
            # Concatenate EPA log files
            if gctf_param['do_EPA'] == 1:
                cmd = f"cat {os.path.join(tomolist['stack_dir'], 'gctf', 'temp')}/*_gctf.log > {os.path.join(tomolist['stack_dir'], 'gctf', st_name)}_EPA.log"
                subprocess.run(cmd, shell=True)
            
            # Concatenate .ctf files
            ctf_stack = np.zeros((gctf_param['boxsize'], gctf_param['boxsize'], n_img))
            for j in range(1, n_img + 1):  # 1-based indexing to match MATLAB
                # String of image number
                num_str = f"{j:0{digits}d}"
                # Read image
                ctf_file = os.path.join(tomolist['stack_dir'], 'gctf', 'temp', f"{st_name}_{num_str}{st_ext}.ctf")
                temp_img, header = sg_mrcread.sg_mrcread(ctf_file)
                ctf_stack[:, :, j-1] = temp_img
            
            sg_mrcwrite.sg_mrcwrite(os.path.join(tomolist['stack_dir'], 'gctf', f"{st_name}.ctf"), ctf_stack, header)
            
            # Convert .star to ctfphaseflip file
            rawtlt_file = os.path.join(tomolist['stack_dir'], f"{st_name}.rawtlt")
            star_file = os.path.join(tomolist['stack_dir'], 'gctf', 'micrographs_all_gctf.star')
            ctfphaseflip_file = os.path.join(tomolist['stack_dir'], 'ctfphaseflip.txt')
            defocii = tomoman_gctf_star_to_ctfphaseflip.tomoman_gctf_star_to_ctfphaseflip(rawtlt_file, star_file, ctfphaseflip_file)
            
            # Cleanup
            cmd = f"rm -rf {os.path.join(tomolist['stack_dir'], 'gctf', 'temp')}"
            subprocess.run(cmd, shell=True)
            print(f"TOMOMAN: Defocus determination of stack \"{tomolist['stack_name']}\" complete!!!")
            
            # Update tomolist
            tomolist['ctf_determined'] = True
            if gctf_param['input_type'] == 'stack':
                tomolist['ctf_determination_algorithm'] = 'GCTF-stack'
            elif gctf_param['input_type'] == 'frames':
                tomolist['ctf_determination_algorithm'] = 'GCTF-frames'
            
            tomolist['determined_defocii'] = defocii
            
            # Save tomolist
            if write_list:
                import pickle
                with open(os.path.join(p['root_dir'], p['tomolist_name']), 'wb') as f:
                    pickle.dump(tomolist, f)
    
    return tomolist