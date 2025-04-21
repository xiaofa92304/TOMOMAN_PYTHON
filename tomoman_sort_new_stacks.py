import os
import datetime
import pickle
import shutil
import numpy as np
from datetime import datetime

def tomoman_sort_new_stacks(p, ov, s, tomolist):
    """
    A function to check the raw_stack_dir for new stacks and .mdoc files, and
    copy them, along with their frames, to new tilt-stack directories. A new
    tomolist will also be generated and filled.
    """
    print("TOMOMAN: Sorting new stacks!!!")
    
    # Get list of .mdoc files
    mdoc_dir = [f for f in os.listdir(p['raw_stack_dir']) if f.endswith('.mdoc')]
    n_stacks = len(mdoc_dir)
    print(f"TOMOMAN: {n_stacks} new .mdoc files found!")
    
    # Initialize mdoc parsing fields
    mdoc_fields = ['TiltAxisAngle', 'TiltAngle', 'ExposureDose', 'ExposureTime', 'TargetDefocus', 'SubFramePath', 'NumSubFrames', 'PixelSpacing', 'DateTime']
    mdoc_field_types = ['num', 'num', 'num', 'num', 'num', 'str', 'num', 'num', 'str']
    
    for i, mdoc_file in enumerate(mdoc_dir):
        # Initialize new tomolist row
        temp_tomolist = tomoman_generate_tomolist(1)
        
        # Write root_dir
        temp_tomolist['root_dir'] = p['root_dir']
        
        # Parse stack number
        stack_num = mdoc_file[len(p['prefix']):-(len(p['raw_stack_ext']) + 5)]
        temp_tomolist['tomo_num'] = int(stack_num)
        
        # Check for .mdoc file
        print(f"TOMOMAN: parsing .mdoc for stack {stack_num}")
        
        # Parse .mdoc
        mdoc_param = parse_mdoc(os.path.join(p['raw_stack_dir'], mdoc_file), mdoc_fields, mdoc_field_types)
        n_tilts = len(mdoc_param)
        
        # Check for raw stack
        raw_stack_name = os.path.join(p['raw_stack_dir'], p['prefix'] + stack_num + p['raw_stack_ext'])
        if not os.path.isfile(raw_stack_name):
            print(f"ACHTUNG!!! Raw stack for tomogram {stack_num} missing!!!")
            if not s['ignore_raw_stacks']:
                print(f"ACHTUNG!!! Skipping stack {stack_num}!!!")
                continue
        
        # Check frames
        frame_names = [None] * n_tilts
        for j in range(n_tilts):
            sub_frame_path = mdoc_param[j]['SubFramePath']
            
            # Check if path is empty
            clean_path = sub_frame_path.replace('\\', '/')  
            try:
                
                filename = os.path.basename(clean_path)
            except Exception as e:
                print(f"Path resolution failure: {sub_frame_path}")
                filename = "ERROR"
            
            frame_names[j] = filename
            # Check for existence of frame
            frame_path = os.path.join(p['raw_frame_dir'], frame_names[j])
            if not os.path.isfile(frame_path):
                print(f"ACHTUNG!!! Frame \"{frame_names[j]}\" missing from stack {stack_num}!!!")
                if not s['ignore_missing_frames']:
                    print(f"ACHTUNG!!! Skipping stack {stack_num}!!!")
                    continue
        
        # Generate new folder
        print(f"Generating directories and moving files for stack {stack_num}!!!")
        tomo_dir = os.path.join(p['root_dir'], p['prefix'] + stack_num + '/')
        print("tomo_dir"+ tomo_dir)
        os.makedirs(tomo_dir, exist_ok=True)
        os.makedirs(os.path.join(tomo_dir, 'frames/'), exist_ok=True)
        temp_tomolist['stack_dir'] = tomo_dir
        temp_tomolist['frame_dir'] = os.path.join(tomo_dir, 'frames/')
        temp_tomolist['frame_names'] = frame_names
        # Move .mdoc file
        shutil.move(os.path.join(p['raw_stack_dir'], mdoc_file), os.path.join(tomo_dir, mdoc_file))
        temp_tomolist['mdoc_name'] = mdoc_file
        
        # Move raw stack
        raw_stack_name = p['prefix'] + stack_num + p['raw_stack_ext']
        src_path = os.path.join(p['raw_stack_dir'], raw_stack_name)  
        dst_path = os.path.join(tomo_dir, raw_stack_name)            

        if os.path.exists(src_path):
            shutil.move(src_path, dst_path)  
            temp_tomolist['raw_stack_name'] = raw_stack_name
        else:
            print(f"WARNING: {src_path} not copied as it does not exist...")
        
        # Move frames
        for j, frame_name in enumerate(frame_names):
            try:
                shutil.move(os.path.join(p['raw_frame_dir'], frame_name), os.path.join(tomo_dir, 'frames/', frame_name))
            except Exception as e:
                print(f"ACHTUNG!!! Error moving {p['raw_frame_dir']}/{frame_name}: {e}")
        
        # Write tilt-axis angle
        if 'tilt_axis_angle' not in ov:
            temp_tomolist['tilt_axis_angle'] = mdoc_param[0]['TiltAxisAngle']
        else:
            temp_tomolist['tilt_axis_angle'] = ov['tilt_axis_angle']

        # Write tilt angles (Order by collection time)
        dt = [datetime.strptime(t['DateTime'], '%d-%b-%y %H:%M:%S') for t in mdoc_param]
        sorted_indices = np.argsort(dt)
        temp_tomolist['collected_tilts'] = [mdoc_param[i]['TiltAngle'] for i in sorted_indices]
        
        # Store camera files
        temp_tomolist['gainref'] = p['gainref']
        temp_tomolist['defects_file'] = p['defects_file']
        temp_tomolist['rotate_gain'] = p['rotate_gain']
        temp_tomolist['flip_gain'] = p['flip_gain']
        
        # Mirror stack
        temp_tomolist['mirror_stack'] = p['mirror_stack']
        
        # Pixelsize
        if 'pixelsize' not in ov:
            is_pixelsize_consistent = True
            first_pixelsize = mdoc_param [0]['pixelsize']
            for d in mdoc_param:
                if d['pixelsize'] != first_pixelsize:
                    is_pixelsize_consistent = False
                    break
                if is_pixelsize_consistent:
                    temp_tomolist['pixelsize'] = mdoc_param[0]['PixelSpacing']
                else:
                    print(f"Achtung!!! {raw_stack_name} has varying pixelsizes!!!")
                    temp_tomolist['pixelsize'] = [p['pixelsize']]
        else:
            temp_tomolist['pixelsize'] = ov['pixelsize']
        
        # Get doses
        total_exposure = np.cumsum([p['ExposureTime'] for p in mdoc_param])
        temp_tomolist['cumulative_exposure_time'] = total_exposure
        if 'dose_rate' not in ov:
            temp_tomolist['dose'] = np.cumsum([p['ExposureDose'] for p in mdoc_param])
        else:
            total_dose = (total_exposure * ov['dose_rate']) / (np.array(temp_tomolist['pixelsize']) ** 2)
            temp_tomolist['dose'] = total_dose
        
        # Target defocus
        is_Target_defocus_consistent = True
        first_Target_defocus = mdoc_param [0]['TargetDefocus']

        for d in mdoc_param:
            if d['TargetDefocus'] != first_Target_defocus:
                is_pixel_spacing_consistent = False
                break

        if is_Target_defocus_consistent:
            temp_tomolist['target_defocus'] = mdoc_param [0]['TargetDefocus']
        else:
            print(f"Achtung!!! {raw_stack_name} has varying target defocii!!!")
            temp_tomolist['target_defocus'] = [p['target_defocus']]
        
        #  NumSubFrames 
        is_num_subframes_consistent = True
        first_num_subframes = mdoc_param  [0]['NumSubFrames']

        for d in mdoc_param:
            if d['NumSubFrames'] != first_num_subframes:
                is_num_subframes_consistent = False
                break

        if is_num_subframes_consistent:
            temp_tomolist['n_frames'] = mdoc_param  [0]['NumSubFrames']
        else:
            temp_tomolist['n_frames'] = [p['n_frames']]
        
        # Append and save tomolist
        tomolist.append(temp_tomolist)
        print(f"Stack {i+1} of {n_stacks} sorted...")
    
    print("TOMOMAN: Stack sorting complete!!!")
    return tomolist

def tomoman_generate_tomolist(num_stacks):
    """
    Generate a template tomolist row.
    """
    return {
        'root_dir': '',
        'stack_dir': '',
        'frame_dir': '',
        'mdoc_name': '',
        'tomo_num': 0,
        'collected_tilts': [],
        'frame_names': [],
        'n_frames': [],
        'pixelsize': 0,
        'image_size':[],
        'cumulative_exposure_time': [],
        'dose': [],
        'target_defocus': [],
        'gainref': '',
        'defects_file': '',
        'rotate_gain': 0,
        'flip_gain': 0,
        'raw_stack_name': '',
        'mirror_stack': '',
        'skip':0,
        'frames_aligned':0,
        'frame_alignment_algorithm':'none',
        'stack_name':'none',
        'clean_stack':0,
        'removed_tilts':[],
        'rawtlt':[],
        'max_tilt':[],
        'min_tilt':[],
        'tilt_axis_angle': 0.0,
        'dose_filtered':0,
        'dose_filtered_stack_name':'none',
        'dose_filter_algorithm':'none',
        'imod_preprocessed':0,
        'ctf_determined':0,
        'ctf_determination_algorithm':'none',
        'determined_defocci':[],
        'stacked_aligned':0
        
    }


def parse_mdoc(mdoc_path, fields, field_types):

    mdoc_data = []
    current_entry = {}
    in_zvalue_block = False  
    
    with open(mdoc_path, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Detect the beginning of the [ZValue] block
            if line.startswith('[ZValue ='):
                
                if in_zvalue_block and current_entry:
                    mdoc_data.append(current_entry)
                    current_entry = {}
                in_zvalue_block = True  
                
            # Only handle the fields within the block
            elif in_zvalue_block:
                for field, ftype in zip(fields, field_types):
                    if line.startswith(field + ' ='):
                        value = line.split('=')[-1].strip()
                        if ftype == 'num':
                            try:
                                value = float(value)
                            except ValueError:
                                pass
                        current_entry[field] = value
                        break  # Exit the loop after finding the field
    
    # Add the last block (if it exists)
    if in_zvalue_block and current_entry:
        mdoc_data.append(current_entry)
    
    return mdoc_data
def parse_mdoc(mdoc_path, mdoc_fields, mdoc_field_types):
 
    mdoc_data = []
    current_entry = {}
    in_zvalue_block = False  
    tilt_axis_angle = None 

    with open(mdoc_path, 'r') as f:
      
        for line in f:
            line = line.strip()
            if line.startswith('[T =   Tilt axis angle = '):
                start_index = line.find('Tilt axis angle =') + len('Tilt axis angle =')
                end_index = line.find(',', start_index) 
                if end_index == -1:
                    end_index = len(line)
                tilt_axis_angle = float(line[start_index:end_index].strip())
                break 

      
        f.seek(0)
        for line in f:
            line = line.strip()
  
            if line.startswith('[ZValue ='):
              
                if in_zvalue_block and current_entry:
                    current_entry['TiltAxisAngle'] = tilt_axis_angle 
                    mdoc_data.append(current_entry)
                    current_entry = {}
                in_zvalue_block = True 

            elif in_zvalue_block:
                for field, ftype in zip(mdoc_fields, mdoc_field_types):
                    if line.startswith(field + ' ='):
                        value = line.split('=')[-1].strip()
                        if ftype == 'num':
                            try:
                                value = float(value)
                            except ValueError:
                                pass
                        current_entry[field] = value
                        break  

    if in_zvalue_block and current_entry:
        current_entry['TiltAxisAngle'] = tilt_axis_angle 
        mdoc_data.append(current_entry)
    
    return mdoc_data

def tomoman_append_tomolist(tomolist, new_tomolist):
    """
    Append a new tomolist row to the existing tomolist.
    """
    return np.vstack((tomolist, new_tomolist))