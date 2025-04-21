# tomoman_run.py
"""
Tomoman is a set of wrapper scripts for preprocessing to tomogram data
collected by SerialEM. 

WW 04-2018
"""

# Inputs

# Directory parameters
p = {
    'root_dir': '/work/home/demo_data_raw_2/'}  # Root folder for dataset; stack directories will be generated here.
p['raw_stack_dir']=p['root_dir'] + 'mdoc/'        # Folder containing raw stacks
p['raw_frame_dir']=p['root_dir'] + 'frames/'      # Folder containing unsorted frames
p['tomolist_name']= 'tomolist_cor3.mat'    # Relative to root_dir
p['log_name']= 'tomoman_cor3.log'        # Relative to root_dir


# Filename parameters
p['prefix'] = 'tomo_'      # Beginning of stack/mdoc names (e.g. stackname is [prefix][tomonum].[raw_stack_ext])
p['digits'] = 3            # Number of digits (i.e. leading zeros; e.g. 02 is digits=2, 002 is digits=3)
p['raw_stack_ext'] = '.mrc'  # File extension of raw stacks

# Data collection parameters
p['gainref'] = p['root_dir'] + './gain.mrc'       # For no gainref, set to 'none'
p['defects_file'] = 'none'   # For no defects_file, set to 'none'
p['rotate_gain'] = 0         # Gain ref rotation
p['flip_gain'] = 0           # Gain ref flip; 0 = none, 1 = up/down, 2 = left/right
p['os'] = 'windows'          # Operating system for data collection. Options are 'windows' and 'linux'
p['mirror_stack'] = 'n'      # Mirror images. For Titan2, use 'y'. For MiKrios set to 'none'

# Overrides (set to '' for no override)
ov = {
    'tilt_axis_angle': 84.63,    # Tilt axis angle in degrees
    'dose_rate': 7.8,            # e/pixel/s
    'pixelsize': 1.21            # Pixel size in Angstroms
}

# Batch mode
batch_mode = 'single'  # 'single' runs a single stack through the whole pipeline before the next stack. 'step' runs all stacks through each step before progressing to the next step.

# Find and sort new stacks?
s = {
    'sort_new': 1,                       # 1 = yes, 0 = no;
    'ignore_raw_stacks': 1,              # Move files even if raw stack is missing
    'ignore_missing_frames': 0           # Move files even if frames are missing
}

# Stack parameters
st = {
    'update_stack': 1,                 # Update stack parameters. 1 = yes, 0 = no; 
    'image_size': [4096, 4096],         # I would suggest 3712, as this allows for a wide range of base2 binning. Images will be padded by copying edge pixels.
    'stack_prefix': 'tomo_',             # Add prefix to stack names. Otherwise, stack names are [tomonum].st.
    'tilt_order': 'ascend',            # Tilt order of the input stacks. Either 'ascend' or 'descend'. It appears that stacks from alignframes are ascending.
    'prealigned': ''                   # If stacks are already frame-aligned, provide name of alignment algorithm. Otherwise, leave empty.
}

# Align frames / generate stack
mc3 = {
    'ali_frames': 1,                     # 1 = yes, 0 = no;
    'force_realign': 0,                  # 1 = yes, 0 = no;
    'input_format': 'eer',               # 'tiff' or 'mrc' or 'eer'
    'dose_filter': 0,                    # Dose filter using MotionCor3
    'dose_filter_suffix': '',            # Suffix to add to dose-filtered stack.
    'ArcDir': '',                        # Path of the archive folder
    'MaskCent': [],                      # Center of subarea that will be used for alignement, default 0 0 corresponding to the frame center.
    'MaskSize': [],                      # The size of subarea that will be used for alignment, default 1.0 1.0 corresponding full size.
    'Patch': [5, 5],                     # Number of patches to be used for patch based alignment, default 0 0 corresponding full frame alignment.
    'Iter': 7,                           # Maximum iterations for iterative alignment, default 5 iterations.
    'Tol': 0.5,                          # Tolerance for iterative alignment, default 0.5 pixel.
    'Bft': [],                           # B-Factor for alignment, default 100.
    'FtBin': [1.0],                      # Binning performed in Fourier space, default 1.0.
    'kV': 300,                         # High tension in kV needed for dose weighting. Default is 300.
    'Throw': [],                         # Throw initial number of frames, default is 0.
    'Trunc': [],                         # Truncate last number of frames, default is 0.
    'Group': 10,                       # Group every specified number of frames by adding them together. The alignment is then performed on the summed frames. By default, no grouping is performed.
    'FmRef': [],                         # Specify which frame to be the reference to which all other frames are aligned. By default (-1) the the central frame is chosen. The central frame is at N/2 based upon zero indexing where N is the number of frames that will be summed, i.e., not including the frames thrown away.
    'OutStack': 0,                       # Write out motion corrected frame stack. Default 0.
    'Align': [],                         # Generate aligned sum (1) or simple sum (0)
    'Tilt': [],                          # Specify the starting angle and the step angle of tilt series. They are required for dose weighting. If not given, dose weighting will be disabled.
    'Mag': [],                           # 1. Correct anisotropic magnification by stretching image along the major axis, the axis where the lower magnification is detected. 2. Three inputs are needed including magnifications along major and minor axes and the angle of the major axis relative to the image x-axis in degree. 3. By default no correction is performed.
    'Crop': [],                          # 1. Crop the loaded frames to the given size. 2. By default the original size is loaded.
    'Gpu': [1, 2]                        # GPU IDs. Default 0. For multiple GPUs, separate IDs by space. For example, -Gpu 0 1 2 3 specifies 4 GPUs.
}

# Clean stacks
c = {
    'clean_stacks': 1,
    'force_cleaning': 0,                 # 1 = yes, 0 = no;
    'clean_binning': 4,                  # Binning to open 3dmod with
    'clean_append': ''                   # Append to name for cleaned stack. Setting blank ('') overwrites old file.
}

# Dose filter stacks
df = {
    'dose_filter': 1,                    # 1 = yes, 0 = no;
    'force_dfilt': 0,                    # 1 = yes, 0 = no;
    'dfilt_append': '_dose-filt',        # Append name to dose-filtered stack. Empty ('') overwrites stack; this is NOT recommended...
    'filter_frames': 0,                  # Dose filter frames instead of images. In order to do this, the OutStack MotionCor2 parameter must have been used to generate aligned frame stacks.
    'preexposure': 0,                    # Pre-exposure prior to initial image collection.
    'a': None,                             # Resolution-dependent critical exposure constant 'a'. Leave emtpy ('') to use default.
    'b': None,                             # Resolution-dependent critical exposure constant 'b'. Leave emtpy ('') to use default.
    'c': None                              # Resolution-dependent critical exposure constant 'c'. Leave emtpy ('') to use default.
}

# IMOD preprocess
imod_param = {
    'imod_preprocess': 1,               # 1 = yes, 0 = no;
    'force_imod': 0,                    # 1 = yes, 0 = no;
    'copytomocoms': 1,                  # Run copytomocoms
    'goldsize': 0,                      # Gold diameter (nm)
    'ccderaser': 1,                     # Run CCD Eraser
    'archiveoriginal': 0,               # Archive and delete original stack
    'coarsealign': 1,                   # Perform coarse alignment 
    'pretilt': 14,                      # Can't be a negative number! Adds a x deg pretilt for hagen sceme collection on lammelas. Automoaticly checks pretilt direction so just put the absolut value. Set to 0 if not needed. 
    'trimming': 200,                    # trimms by the given amount of pixels in x and y (usefull for patchtarcking), if not needed set to 0 
    'coarsealignbin': 4,                # Bin factor for coarse alignment
    'coarseantialias': -1,              # Antialiasing filter for coarse alignment
    'convbyte': '/',                    # Convert to bytes: '/' = no, '0' = yes
    'autoseed': 0,                      # Run autofidseed and beadtrack
    'localareatracking': 1,             # Local area bead tracking (1=yes,0=no)
    'localareasize': 1000,              # Size of local area
    'sobelfilter': 1,                   # Use Sobel filter (1=yes,0=no)
    'sobelkernel': 1.5,                 # Sobel filter kernel (default 1.5)
    'n_rounds': 2,                      # Number of rounds of tracking in run (default = 2)
    'n_runs': 2,                        # Number of times to run beadtrack (default = 2)
    'two_surf': 2,                      # Track beads on two surfaces (1=yes,0=no) 
    'n_beads': 100,                     # Target number of beads
    'adjustsize': 1,                    # Adjust size of beads based on average bead size (1=yes,0=no) 
    'patchtrack': 1,                    # Run patchtracking of your Lammela
    'patchsizeX': 300,                  # Size of patch used in X
    'patchsizeY': 300,                  # Size of patch used in Y
    'OverlapOfPatchesXandY': 0.45,      # Overlap of patches in x and y
    'IterateCorrelations': 4,           # Number of Iterations 
    'adjustTiltAngles': 1,              # Bool for 'Run again with tilt angle offset from Tiltalign'
    'Align': 1,                         # Run fine alignment steps from etomo
    'RobustFitting': 1,                 # Whether to use robust fitting to downweight some points(bool)
    'KFactorScaling': 0.9,              # Factor that determines how many points are downwieghted (the lower the more, float numb)
    'RotOption': -1,                    # Type of rotation solution (1 solve all; 3 group; -1 solve one; 0 fix)
    'TiltOption': 0,                    # Type of tilt angle solution (1 solve all; 5 group; 0 fix)
    'MagOption': 0,                     # Type of magnification solution (1 solve all; 3 group; 0 fix)
    'positioning': 0                    # Just creats a bin 8 tomo to do positoining on (Bool)
}

# GCTF
gctf_param = {
    'run_gctf': 0,                     # 1 = yes, 0 = no;
    'force_gctf': 0,                   # 1 = yes, 0 = no;
    'input_type': 'stack',             # What to use as input for gctf. 'stack' for image stack or 'frames' for raw frames.
    
    # Normal options(should specify)
    'kV': 300,                         # High tension in Kilovolt, typically 300, 200 or 120
    'cs': 2.7,                         # Spherical aberration, in millimeter
    'ac': 0.07,                        # Amplitude contrast; normal range 0.04~0.1; pure ice 0.04, carbon 0.1; but doesn't matter too much if using wrong value
    
    # Phase plate options:
    'determine_pshift': 0,             # Determine phase shift. 1 = yes, 0 = no. (default = 0)
    'phase_shift_L': 0.0,              # User defined phase shift, lowest phase shift, in degree; typically, ~90.0 for micrographs using phase plate
    'phase_shift_H': 180.0,            # User defined phase shift, highest phase shift, final range will be (phase_shift_L, phase_shift_H)
    'phase_shift_S': 10.0,             # User defined phase shift search step; don't worry about the accuracy; this is just the search step, Gctf will refine the phase shift anyway.
    'phase_shift_T': 1,                # Phase shift target in the search; 1: CCC; 2: resolution limit;
    
    # Additional options (Note: TOMOMAN automatically sets the defocus low and high parameters {defL,defH} using the defocus_width and the target_defocus.)
    'dstep': 14.0,                     # Detector size in micrometer; don't worry if unknown; just use default. (default = 14.0)
    'defWidth': 20000,                 # Range to search around target defocus (Angstroms); i.e. range will be (TargetDefocus - defWidth) -- (TargetDefocus + defWidth).
    'defS': 500,                       # Step of defocus value used to search, in angstrom (default = 500)
    'astm': 1000,                      # Estimated astigmation in angstrom, don't need to be accurate, within 0.1~10 times is OK (default = 1000)
    'bfac': 150,                       # Bfactor used to decrease high resolution amplitude,A^2; NOT the estimated micrograph Bfactor! suggested range 50~300 except using 'REBS method'. (default = 150)
    'resL': 50,                        # Lowest Resolution to be used for search, in angstrom (default = 50)
    'resH': 4,                         # Highest Resolution to be used for search, in angstrom (default = 4)
    'boxsize': 512,                    # Boxsize in pixel to be used for FFT, 512 or 1024 highly recommended (default = 1024)
    
    # Advanced additional options:
    'do_EPA': 1,                       # 1: Do Equiphase average; 0: Don't do; only for nice output, will NOT be used for CTF determination. (default = 0)
    'EPA_oversmp': 4,                  # Over-sampling factor for EPA. (default = 4)
    'overlap': 0.5,                    # Overlapping factor for grid boxes sampling, for boxsize=512, 0.5 means 256 pixels overlapping (default = 0.5)
    'convsize': 85,                    # Boxsize to be used for smoothing, suggested 1/10 ~ 1/20 of boxsize in pixel, e.g. 40 for 512 boxsize (default = 85)
    
    # High resolution refinement options:
    'do_Hres_ref': 0,                  # Whether to do High-resolution refinement or not, very useful for selecting high quality micrographs (default = 0)
    'Href_resL': 15.0,                 # Lowest Resolution to be used for High-resolution refinement, in angstrom (default = 15.0)
    'Href_resH': 4.0,                  # Highest Resolution to be used for High-resolution refinement, in angstrom (default = 4.0)
    'Href_bfac': 50,                   # Bfactor to be used for High-resolution refinement,A^2 NOT the estimated micrograph Bfactor! (default = 50)
    
    # Bfactor estimation options:
    'B_resL': 15.0,                    # Lowest resolution for Bfactor estimation; This output Bfactor is the real estimation of the micrograph (default = 15)
    'B_resH': 6.0,                     # Highest resolution for Bfactor estimation (default = 6)
    
    # Movie options to calculate defocuses of each frame:
    'do_mdef_refine': 0,               # Whether to do CTF refinement of each frames, by default it will do averaged frames. Not quite useful at the moment, but maybe in future. (default = 0)
    'mdef_aveN': 1,                    # Average number of movie frames for movie or particle stack CTF refinement (default = 1)
    'mdef_fit': 0,                     # 0: no fitting; 1: linear fitting defocus changes in Z-direction (default = 0)
    'mdef_ave_type': 0,                # 0: coherent average, average FFT with phase information(suggested for movies); 1: incoherent average, only average amplitude(suggested for particle stack); (default = 0)
    
    # CTF refinement options(to refine user provided CTF parameters):
    'refine_input_ctf': 0,             # 1: to refine user provided CTF; 0: By default Gctf will NOT refine user-provided CTF parameters but do ab initial determination, even if the '--input_ctfstar' is provided; (default = 0)
    'input_ctfstar': 'none',           # Input file name with previous CTF parameters
    'defU_init': 20000.0,              # User input initial defocus_U, only for single micrograph, use '--input_ctfstar' for multiple micrographs. (default = 20000)
    'defV_init': 20000.0,              # User input initial defocus_V, only for single micrograph, use '--input_ctfstar' for multiple micrographs. (default = 20000)
    'defA_init': 0.0,                  # User input initial defocus_Angle, only for single micrograph, use '--input_ctfstar' for multiple micrographs. (default = 0)
    'B_init': 200.0,                   # User input initial Bfactor, only for single micrograph, use '--input_ctfstar' for multiple micrographs. (default = 200)
    'defU_err': 500.0,                 # Estimated error of user input initial defocus_U, unlike defU_init, this will be effective for all micrographs. (default = 500)
    'defV_err': 500.0,                 # Estimated error of user input initial defocus_V, unlike defV_init, this will be effective for all micrographs. (default = 500)
    'defA_err': 15.0,                  # Estimated error of user input initial defocus_Angle, unlike defA_init, this will be effective for all micrographs.
    'B_err': 50.0,                     # Estimated error of user input initial Bfactor, unlike B_init, this will be effective for all micrographs. (default = 50)
    
    # Validation options:
    'do_validation': 0,                # Whether to validate the CTF determination. (default = 0)
    
    # CTF output file options:
    'ctfout_resL': 100.0,              # Lowest resolution for CTF diagnosis file. NOTE this only affects the final output of .ctf file, nothing related to CTF determination. (default = 100)
    'ctfout_resH': '',                 # Highest resolution for CTF diagnosis file, ~Nyquist by default.
    'ctfout_bfac': 50,                 # Bfactor for CTF diagnosis file. NOTE this only affects the final output of .ctf file, nothing related to CTF determination. (default = 50)
    
    # I/O options:
    'input_ctfstar': '',               # Input star file (must be star file) containing the raw micrographs and CTF information for further refinement.
    'boxsuffix': '',                   # Input .box/.star in EMAN/Relion box format, used for local refinement
    'ctfstar': '',                     # Output star files to record all CTF parameters. Use 'NULL' or 'NONE' to skip writing out the CTF star file.
    'logsuffix': '',                   # Output suffix to be used for log files. (default = '_gctf.log')
    'write_local_ctf': 0,              # Whether to write out a diagnosis power spectrum file for each particle.
    'plot_res_ring': 1,                # Whether to plot an estimated resolution ring on the final .ctf diagnosis file
    'do_unfinished': [],               # Specify this option to continue processing the unfinished, otherwise it will overwrite everything.
    'skip_check_mrc': [],              # Specify this option to skip checking the MRC file format. Sometimes, there are special MRC that the file size does not match head information. To force Gctf run on such micrograph, specify this option might help to solve the problem.
    'skip_check_gpu': [],              # Specify this option to skip checking the GPUs.
    'gid': 3                           # GPU id, normally it's 0, use gpu_info to get information of all available GPUs.
}

import os
import sys
import pickle

log_path = os.path.join(p['root_dir'], p['log_name'])

os.makedirs(p['root_dir'], exist_ok=True)

# Initialize
diary = open(os.path.join(p['root_dir'], p['log_name']), 'w')

print('TOMOMAN Initializing!!!', file=diary)

# Check extension
if not p['raw_stack_ext'].startswith('.'):
    p['raw_stack_ext'] = '.' + p['raw_stack_ext']

# 检查操作系统
if p['os'] not in {'windows', 'linux'}:
    sys.exit(f'ACHTUNG!!! Invalid p.os parameter!!! Only "windows" and "linux" supported!!!')

# 读取tomolist
tomolist_path = os.path.join(p['root_dir'], p['tomolist_name'])

if os.path.exists(tomolist_path):
    print('TOMOMAN: Old tomolist found... Loading tomolist!!!')
    with open(tomolist_path, 'rb') as f:
        tomolist = pickle.load(f)
else:
    print('TOMOMAN: No tomolist found... Generating new tomolist!!!')
    tomolist = []  

import shutil
import sys

# Check dependencies
dependencies = ["3dmod", "newstack"]

# Check dependencies
for dep in dependencies:
    if shutil.which(dep) is None:
        sys.exit(f"ACHTUNG!!! {dep} not found!!! Source the package prior to running Python!!!")

import tomoman_sort_new_stacks as sort

# Sort new stacks
if s["sort_new"] == 1:
    tomolist = sort.tomoman_sort_new_stacks(p, ov, s, tomolist)
    # save tomolist (MATLAB's save() corresponds to Python's pickle.dump)
    tomolist_path = os.path.join(p["root_dir"], p["tomolist_name"])
    with open(tomolist_path, "wb") as f:
        pickle.dump(tomolist, f)

# Run pipeline!!!

# Set batchmode settings
n_tilts = len(tomolist)
if batch_mode == 'single':
    b_size = 1
    write_list = False
    t = 1
elif batch_mode == 'step':
    b_size = n_tilts
    write_list = True
    t = list(range(1, n_tilts + 1))

import tomoman_stack_param as stack

import tomoman_motioncor3_newstack_modi_GQ as modi

import tomoman_clean_stacks as tomoman_clean_stacks

import tomoman_exposure_filter as tomoman_exposure_filter

import tomoman_imod_preprocess_mod as tomoman_imod_preprocess_mod

import tomoman_gctf as tomoman_gctf

while t <= n_tilts:
    # Check tomogram parameters
    if st['update_stack'] == 1:
        tomolist[t-1] = stack.tomoman_stack_param(tomolist[t-1], st)
        # Write tomolist
        with open(os.path.join(p['root_dir'], p['tomolist_name']), 'wb') as f:
            pickle.dump(tomolist, f)
    
    # Align frames
    if mc3['ali_frames'] == 1:
        # Align frames and generate stack
        tomolist[t-1] = modi.tomoman_motioncor3_newstack_modi_GQ(tomolist[t-1], p, st, mc3, write_list)
        # Write tomolist
        with open(os.path.join(p['root_dir'], p['tomolist_name']), 'wb') as f:
            pickle.dump(tomolist, f)
    
    # Clean stacks
    if c['clean_stacks'] == 1:
        # Clean stacks
        tomolist[t-1] = tomoman_clean_stacks.tomoman_clean_stacks(tomolist[t-1], p, c, st, write_list, skip_3dmod=False)
        # Save tomolist
        with open(os.path.join(p['root_dir'], p['tomolist_name']), 'wb') as f:
            pickle.dump(tomolist, f)
    
    # Apply dose filter
    if df['dose_filter'] == 1:
        # Dose filter
        tomolist[t-1] = tomoman_exposure_filter.tomoman_exposure_filter(tomolist[t-1], p, st, df, write_list)
        # Save tomolist
        with open(os.path.join(p['root_dir'], p['tomolist_name']), 'wb') as f:
            pickle.dump(tomolist, f)
    
    # IMOD preprocess
    if imod_param['imod_preprocess'] == 1:
        # Preprocess
        tomolist[t-1] = tomoman_imod_preprocess_mod.tomoman_imod_preprocess_mod_GQ(tomolist[t-1], p, imod_param, write_list)
        # Save tomolist
        with open(os.path.join(p['root_dir'], p['tomolist_name']), 'wb') as f:
            pickle.dump(tomolist, f)
    
    # GCTF
    if gctf_param['run_gctf'] == 1:
        # Preprocess
        tomolist[t-1] = tomoman_gctf.tomoman_gctf(tomolist[t-1], p, gctf_param, write_list)
        # Save tomolist
        with open(os.path.join(p['root_dir'], p['tomolist_name']), 'wb') as f:
            pickle.dump(tomolist, f)
    
    # Increment counter
    t += b_size

# Close diary file
diary.close()