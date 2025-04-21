import numpy as np
import math

def tomoman_gctf_star_to_ctfphaseflip(tlt_name, star_name, out_name):
    """
    A function to take a GCTF star file and convert it to the format required
    for IMOD's ctfphaseflip option.
    
    Parameters:
    -----------
    tlt_name : str
        Path to the .tlt file
    star_name : str
        Path to the GCTF .star file
    out_name : str
        Path to the output file
        
    Returns:
    --------
    defocii : numpy.ndarray
        Array containing defocus values (U, V, angle) for each tilt
    """
    
    # Read tlt file
    tlt = np.loadtxt(tlt_name)
    n_tilts = tlt.shape[0]
    
    # Read star file
    star = tomoman_star_read(star_name)
    if n_tilts != len(star):
        raise ValueError(f"ACHTUNG!!! Incorrect number of tilts! .tlt file contains {n_tilts} while .star contains {len(star)}!!!")
    
    # Initialize output file
    digits = math.ceil(math.log10(n_tilts + 1))
    format_spec = f"%{digits}d    %{digits}d    %6.2f    %6.2f    %4d    %4d    %3.1f\n"
    
    with open(out_name, 'w') as output:
        output.write("1  0 0. 0. 0  3\n")
        
        # Write output
        for i in range(1, n_tilts + 1):  # 1-based indexing to match MATLAB
            # Output line
            line = [0] * 7
            line[0:2] = [i, i]
            line[2:4] = [tlt[i-1], tlt[i-1]]  # Python is 0-indexed
            line[4] = round(star[i-1]['rlnDefocusV'] / 10)
            line[5] = round(star[i-1]['rlnDefocusU'] / 10)
            line[6] = star[i-1]['rlnDefocusAngle']
            
            # Write output
            output.write(format_spec % tuple(line))
    
    # Return defocus table
    defocii = np.zeros((n_tilts, 3))
    defocii[:, 0] = [item['rlnDefocusU'] for item in star] / 10000
    defocii[:, 1] = [item['rlnDefocusV'] for item in star] / 10000
    defocii[:, 2] = [item['rlnDefocusAngle'] for item in star]
    
    return defocii