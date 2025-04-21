def sg_append_mrc_label(header, new_label, max_labels=10):
    '''
    Enhanced tag append function
    :param max_labels: Maximum label storage quantity (default: 10)
    New features:
    Automatically trim whitespace characters
    Support multi-line label segmentation
    Type safety check
    '''

    if not isinstance(header, dict):
        raise TypeError("header 必须是字典类型")
    
 
    header.setdefault('labl', [])
    header.setdefault('nlabl', 0)
    
 
    for line in new_label.split('\n'):
    
        clean_line = line.strip()[:80]
        if clean_line:
            header['labl'].append(clean_line)
    
  
    header['labl'] = header['labl'][-max_labels:]
    header['nlabl'] = len(header['labl'])
    
    return header