import os
import subprocess
import tomoman_motioncor3_argument_parser as argument

def tomoman_motioncor3_batch_wrapper_modi_GQ(input_names, output_names, tomolist, mc3):
    """
    A wrapper function for batch stack processing of images using MotionCor3.

    Parameters:
    input_names (list): A list of input file names.
    output_names (list): A list of output file names.
    tomolist (dict): A dictionary containing stack information.
    mc3 (dict): A dictionary containing parameters.

    Returns:
    None
    """
    
    # Check names
    if isinstance(input_names, list) and isinstance(output_names, list):
        n_img = len(input_names)
        if n_img != len(output_names):
            raise ValueError('Number of input names does not match output names!!!')
    else:
        raise ValueError('Input and output names must be lists!!!')

    # Check input format
    input_format = mc3.get('input_format', 'mrc')
    if input_format not in ['tiff', 'mrc', 'eer']:
        raise ValueError('Invalid input_format!!!')

    in_str = f'-In{input_format.upper()} ' if input_format != 'mrc' else '-InMrc '

    # Gainref
    if 'gainref' in tomolist and tomolist['gainref'] != 'none':
        gain_str = f' -Gain {tomolist["gainref"]} '
        if 'rotate_gain' in tomolist:
            gain_str += f' -RotGain {tomolist["rotate_gain"]} '
        if 'flip_gain' in tomolist:
            gain_str += f' -FlipGain {tomolist["flip_gain"]} '
    else:
        gain_str = ''

    # Parse other parameters
    other_param = argument.tomoman_motioncor3_argument_parser(mc3)

    # Run motioncor3
    for i in range(n_img):
        # Check for dose filtering
        if 'dose_filter' in mc3 and mc3['dose_filter']:
            pixelsize_str = f' -PixSize {tomolist["pixelsize"]} '
            init_dose = 0 if i == 0 else tomolist['dose'][i-1]
            init_dose_str = f' -InitDose {init_dose} '
            img_dose = tomolist['dose'][i] - (init_dose if i > 0 else 0)
            dpf_str = f' -FmDose {img_dose / tomolist["n_frames"]} '
            dosefilter_str = f'{pixelsize_str}{init_dose_str}{dpf_str}'
        else:
            dosefilter_str = ''

        # Construct command
        command = f'MotionCor3 {in_str}{input_names[i]} -OutMrc {output_names[i]} -LogFile {output_names[i]}.log {gain_str}{dosefilter_str}{other_param}'

        # Run command
        print(f'Running MotionCor3: {command}')
        subprocess.run(command, shell=True)
