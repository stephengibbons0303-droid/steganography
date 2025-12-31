import numpy as np
from PIL import Image, ImageOps

def load_image(image_file) -> Image.Image:
    """
    Loads an image and ensures EXIF orientation is applied.
    """
    img = Image.open(image_file)
    img = ImageOps.exif_transpose(img)
    return img

def crop_same_size(image1: Image.Image, image2: Image.Image):
    """
    Crops two images to the smallest common width and height.
    """
    w1, h1 = image1.size
    w2, h2 = image2.size
    
    min_w = min(w1, w2)
    min_h = min(h1, h2)
    
    # Crop from top-left (0,0)
    img1_cropped = image1.crop((0, 0, min_w, min_h))
    img2_cropped = image2.crop((0, 0, min_w, min_h))
    
    return img1_cropped, img2_cropped

def encode_image(cover_img: Image.Image, hidden_img: Image.Image, n_bits: int = 2) -> Image.Image:
    """
    Hides 'hidden_img' inside 'cover_img' using the 'n_bits' least significant bits.
    """
    # Ensure images are the same size
    cover_crop, hidden_crop = crop_same_size(cover_img, hidden_img)
    
    # Convert to NumPy arrays (handle RGBA by converting to RGB for simplicity, or keep alpha)
    # For now, let's force RGB to avoid alpha channel complexity in basic steganography
    cover_arr = np.array(cover_crop.convert("RGB"))
    hidden_arr = np.array(hidden_crop.convert("RGB"))
    
    # --- Logic Verification ---
    # JS: factorChop = 2^bitsHide
    # JS: floor(val / factorChop) * factorChop -> Clears last 'n' bits.
    # In bitwise: val & ~(2^n - 1)
    # Example n=2: 2^2=4. Mask = 11111100 (255 - 3). 
    
    # Cleared Cover: Keep top (8-n) bits
    # We can do this by bitwise AND with a mask that has zeros in the last n spots
    # Mask for clearing last n bits: 255 - (2^n - 1)
    # E.g. n=2 -> 2^n=4 -> 2^n-1=3 (00000011). ~3 = 11111100.
    shift_down_amt = 8 - n_bits
    
    # 1. Clear least significant bits of cover
    # Right shift then Left shift is equivalent to floor/multiply in JS
    # cover_cleared = (cover >> n_bits) << n_bits # Actually no, we want to clear the BOTTOM
    # JS: floor(pix/4)*4 -> clears bottom 2.  (11111100)
    # Using bitmask is safer/clearer
    mask_cover = 0xFF & (0xFF << n_bits) 
    cover_cleared = cover_arr & mask_cover
    
    # 2. Prepare hidden image
    # JS: shift(im) -> floor(px / factorHide). factorHide = 2^(8-n)
    # This takes the top n bits of hidden and moves them to bottom n positions.
    # Example n=2: factorHide = 2^6 = 64. 
    # Top 2 bits (b7, b6) move to (b1, b0).
    hidden_shifted = hidden_arr >> shift_down_amt
    
    # 3. Combine
    combined = cover_cleared + hidden_shifted
    
    return Image.fromarray(combined.astype('uint8'))

def decode_image(encoded_img: Image.Image, n_bits: int = 2) -> Image.Image:
    """
    Extracts the hidden image from the 'encoded_img' using the 'n_bits' least significant bits.
    """
    encoded_arr = np.array(encoded_img.convert("RGB"))
    
    # JS: factorChop = 2^n
    # JS: (val % factorChop) * factorHide
    # val % factorChop -> extracts bottom n bits.
    # * factorHide (2^(8-n)) -> shifts them to top.
    
    # 1. Extract bottom n bits
    mask_bottom = (1 << n_bits) - 1
    extracted_bits = encoded_arr & mask_bottom
    
    # 2. Shift to top
    shift_up_amt = 8 - n_bits
    decoded_arr = extracted_bits << shift_up_amt
    
    return Image.fromarray(decoded_arr.astype('uint8'))
