import sg_default_mrc_header_fields as default
def sg_generate_mrc_header(header_fields=None):
    '''Generate the default MRC header information'''
    if header_fields is None:
        header_fields = default.sg_default_mrc_header_fields()
    
    header = {}
    for field_name, default_value in header_fields:
        header[field_name] = default_value
    
    return header