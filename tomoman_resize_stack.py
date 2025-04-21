import numpy as np

def tomoman_resize_stack(stack, x, y, edgepadding=False):
    """
    Adjust the image stack to the target XY size.
    If the target size is smaller than the original size, the image will be cropped.
    If the target size is larger than the original size, the image can be filled with edge pixels or with the average gray value.
    Parameter:
    stack: Input the image stack, with the shape of (in_x, in_y, n_img)
    x: Target X size
    y: Target Y size
    edgepadding: Whether to fill with edge pixels (default is False, filled with average gray value)
    Return:
    new_stack: The image stack after resizing


    """
   
    in_x, in_y, n_img = stack.shape

    if (in_x == x) and (in_y == y):
        return stack
    
    new_stack = np.zeros((x, y, n_img), dtype=stack.dtype)
    
    pad_x = False
    if in_x == x:
        nx1, nx2, ox1, ox2 = 0, x, 0, x
    elif in_x > x:
        nx1, nx2 = 0, x
        ox1 = int((in_x - x) / 2)
        ox2 = ox1 + x
    elif in_x < x:
        nx1 = int((x - in_x) / 2)
        nx2 = nx1 + in_x
        ox1, ox2 = 0, in_x
        pad_x = True
    
    pad_y = False
    if in_y == y:
        ny1, ny2, oy1, oy2 = 0, y, 0, y
    elif in_y > y:
        ny1, ny2 = 0, y
        oy1 = int((in_y - y) / 2)
        oy2 = oy1 + y
    elif in_y < y:
        ny1 = int((y - in_y) / 2)
        ny2 = ny1 + in_y
        oy1, oy2 = 0, in_y
        pad_y = True
    
    for i in range(n_img):
       
        old_img = stack[ox1:ox2, oy1:oy2, i]
        
        new_img = np.ones((x, y), dtype=stack.dtype) * np.mean(old_img)
        new_img[nx1:nx2, ny1:ny2] = old_img
        
       
        if edgepadding:
         
            if pad_x:
               
                if nx1 > 0:
                    new_img[0:nx1, ny1:ny2] = np.tile(old_img[0:1, :], (nx1, 1))
               
                if nx2 < x:
                    new_img[nx2:x, ny1:ny2] = np.tile(old_img[-1:, :], (x - nx2, 1))
            
            if pad_y:
          
                if ny1 > 0:
                    new_img[nx1:nx2, 0:ny1] = np.tile(old_img[:, 0:1], (1, ny1))
            
                if ny2 < y:
                    new_img[nx1:nx2, ny2:y] = np.tile(old_img[:, -1:], (1, y - ny2))
 
        new_stack[:, :, i] = new_img
    
    return new_stack