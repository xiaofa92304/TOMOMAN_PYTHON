def tomoman_motioncor3_argument_parser(param):
    
    # MotionCor3 参数定义 (参数名, 类型)
    parameters = [
        ('ArcDir', 'str'),
        ('MaskCent', 'float'),
        ('MaskSize', 'float'),
        ('Patch', 'int'),
        ('Iter', 'int'),
        ('Tol', 'float'),
        ('Bft', 'float'),
        ('FtBin', 'float'),
        ('kV', 'float'),
        ('Throw', 'int'),
        ('Trunc', 'int'),
        ('Group', 'int'),
        ('FmRef', 'int'),
        ('OutStack', 'int'),
        ('Align', 'int'),
        ('Tilt', 'int'),
        ('Mag', 'float'),
        ('Crop', 'int'),
        ('Gpu', 'int')
    ]
    
    param_list = []
    
    # Convert the parameter definitions into a dictionary for easy query
    param_def = {name: dtype for name, dtype in parameters}
    
    # Traverse the input parameters
    for name, value in param.items():
        # Skip the undefined parameters
        if name not in param_def:
            continue
        
        # Skip null values
        if value is None:
            continue
            
        dtype = param_def[name]
        
        # Format the parameters according to the type
        if dtype == 'str':
            param_str = f" -{name} {value} "
        elif dtype == 'int':
            
            if isinstance(value, (list, tuple)):
                formatted = ' '.join(f"{int(v)}" for v in value)
            else:
                formatted = f"{int(value)}"
            param_str = f" -{name} {formatted} "
        elif dtype == 'float':
            if isinstance(value, (list, tuple)):
                formatted = ' '.join(f"{float(v):f}" for v in value)
            else:
                formatted = f"{float(value):f}"
            param_str = f" -{name} {formatted} "
        else:
            continue  
            
        param_list.append(param_str.strip()) 
    
    return ' '.join(param_list)