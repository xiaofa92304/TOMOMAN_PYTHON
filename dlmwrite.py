import os
import numpy as np

def dlmwrite(filename, m, *args, **kwargs):
    """
 
    Write matrices or arrays to text files, supporting delimiter and offset Settings
    Parameter:
    filename: Output the filename
    m: The matrix or array to be written to
    Optional parameters (by position or keyword):
    delimiter: Delimiter, default is ','
    roffset: Row offset, default is 0
    coffset: Column offset, default is 0
    precision: Numerical accuracy, default is 5
    append: Whether to append mode, default is False
    newline: Newline character type, 'pc' or 'unix', default is the system default
    """
    # parameter calibration
    if len(args) < 1:
  
        dlm = ','
        r = 0
        c = 0
        precn = 5
        append_mode = False
        nl = os.linesep
    else:
     
        dlm, r, c, nl, precn, append_mode = parse_input(args, kwargs)
    
    if not isinstance(filename, str):
        raise TypeError("The file name must be a string")
    
    # Process the input data
    try:
        
        if isinstance(m, list):
            m = np.array(m)
        
        if isinstance(m, str):
          
            is_char_array = True
            br = 1
            bc = len(m)
            m = [m] 
        else:
           
            is_char_array = False
            m = np.asarray(m)
            if m.ndim == 1:
                m = m.reshape(1, -1) 
            br, bc = m.shape
    except Exception as e:
        raise e
    

    mode = 'a' if append_mode else 'w'
    with open(filename, mode) as f:
    
        for _ in range(r):
            f.write(dlm * (bc + c - 1) + nl)
        
        for i in range(br):
           
            if c > 0:
                f.write(dlm * c)
            
            if is_char_array:
             
                row_data = m[i]
                if isinstance(row_data, str):
                    chars = list(row_data)
                else:
                    chars = row_data
                
                f.write(dlm.join(chars))
            else:
           
                row = m[i]
                row_str = []
                
                for j in range(bc):
                    val = row[j]
                    
                
                    if np.iscomplex(val):
                        if isinstance(precn, int):
                       
                            fmt = f"{{:.{precn}g}}{{:+.{precn}g}}j"
                            s = fmt.format(val.real, val.imag)
                        else:
                     
                            cpx_prec = precn + precn.replace('%', '%+') + 'j'
                            s = cpx_prec.format(val.real, val.imag)
                    else:
                 
                        if isinstance(precn, int):
                     
                            fmt = f"{{:.{precn}g}}"
                            s = fmt.format(val)
                        else:
                       
                            s = precn.format(val)
                    
                    row_str.append(s)
                
                f.write(dlm.join(row_str))
            

            f.write(nl)


def parse_input(args, kwargs):
   
    dlm = ','
    r = 0
    c = 0
    precn = 5
    append_mode = False
    nl = os.linesep
    
    if kwargs:
        if 'delimiter' in kwargs:
            dlm = set_dlm(kwargs['delimiter'])
        if 'roffset' in kwargs:
            r = set_roffset(kwargs['roffset'])
        if 'coffset' in kwargs:
            c = set_coffset(kwargs['coffset'])
        if 'precision' in kwargs:
            precn = kwargs['precision']
        if 'append' in kwargs:
            append_mode = bool(kwargs['append'])
        if 'newline' in kwargs:
            nl = set_newline(kwargs['newline'])
    
    if args:
        
        if len(args) > 0 and args[0] is not None:
            dlm = set_dlm(args[0])
        
        
        if len(args) > 1 and args[1] is not None:
            r = set_roffset(args[1])
        
        
        if len(args) > 2 and args[2] is not None:
            c = set_coffset(args[2])
    
    return dlm, r, c, nl, precn, append_mode


def set_dlm(dlm):
    if isinstance(dlm, str) and len(dlm) <= 1:
        return dlm
    else:
        raise ValueError(f"The delimiter must be a single character: {dlm}")


def set_newline(nl_type):
    '''Set the line break character'''
    if isinstance(nl_type, str):
        if nl_type.lower() == 'pc':
            return '\r\n'
        elif nl_type.lower() == 'unix':
            return '\n'
        else:
            raise ValueError("The newline character type must be 'pc' or 'unix ''")
    else:
        raise TypeError("The newline character type must be a string")


def set_roffset(offset):
    '''Set the line offset'''
    if isinstance(offset, (int, float)):
        return int(offset)
    else:
        raise TypeError(f"The row offset must be numerical: {offset}")


def set_coffset(offset):
    '''Set column offset'''
    if isinstance(offset, (int, float)):
        return int(offset)
    else:
        raise TypeError(f"Column offsets must be numerical: {offset}")