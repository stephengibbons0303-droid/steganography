import numpy as np
from PIL import Image, ImageOps
import hashlib

def load_image(image_file) -> Image.Image:
    """
    Loads an image and ensures EXIF orientation is applied.
    """
    img = Image.open(image_file)
    img = ImageOps.exif_transpose(img)
    return img

def _get_seed_from_password(password: str) -> int:
    """
    Convert a password string to a deterministic integer seed.
    """
    hash_bytes = hashlib.sha256(password.encode('utf-8')).digest()
    return int.from_bytes(hash_bytes[:4], 'big')

def scramble_image(img_array: np.ndarray, password: str) -> np.ndarray:
    """
    Scramble pixel positions using a password-seeded permutation.
    The image becomes random noise without the password.
    """
    shape = img_array.shape
    flat = img_array.flatten()

    # Create deterministic permutation from password
    seed = _get_seed_from_password(password)
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(len(flat))

    # Apply permutation
    scrambled = flat[permutation]
    return scrambled.reshape(shape)

def unscramble_image(img_array: np.ndarray, password: str) -> np.ndarray:
    """
    Reverse the scrambling using the same password.
    """
    shape = img_array.shape
    flat = img_array.flatten()

    # Recreate the same permutation
    seed = _get_seed_from_password(password)
    rng = np.random.default_rng(seed)
    permutation = rng.permutation(len(flat))

    # Create inverse permutation
    inverse_perm = np.argsort(permutation)

    # Apply inverse permutation
    unscrambled = flat[inverse_perm]
    return unscrambled.reshape(shape)

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

def encode_image(cover_img: Image.Image, hidden_img: Image.Image, n_bits: int = 2, password: str = None) -> Image.Image:
    """
    Hides 'hidden_img' inside 'cover_img' using the 'n_bits' least significant bits.
    If password is provided, scrambles the hidden image first for security.
    """
    # Ensure images are the same size
    cover_crop, hidden_crop = crop_same_size(cover_img, hidden_img)

    # Convert to NumPy arrays
    cover_arr = np.array(cover_crop.convert("RGB"))
    hidden_arr = np.array(hidden_crop.convert("RGB"))

    # Scramble hidden image if password provided
    if password:
        hidden_arr = scramble_image(hidden_arr, password)

    shift_down_amt = 8 - n_bits

    # 1. Clear least significant bits of cover
    mask_cover = 0xFF & (0xFF << n_bits)
    cover_cleared = cover_arr & mask_cover

    # 2. Prepare hidden image - take top n_bits and shift to bottom
    hidden_shifted = hidden_arr >> shift_down_amt

    # 3. Combine
    combined = cover_cleared + hidden_shifted

    return Image.fromarray(combined.astype('uint8'))

def decode_image(encoded_img: Image.Image, n_bits: int = 2, password: str = None) -> Image.Image:
    """
    Extracts the hidden image from the 'encoded_img' using the 'n_bits' least significant bits.
    If password is provided, unscrambles the extracted image.
    """
    encoded_arr = np.array(encoded_img.convert("RGB"))

    # 1. Extract bottom n bits
    mask_bottom = (1 << n_bits) - 1
    extracted_bits = encoded_arr & mask_bottom

    # 2. Shift to top
    shift_up_amt = 8 - n_bits
    decoded_arr = extracted_bits << shift_up_amt

    # Unscramble if password provided
    if password:
        decoded_arr = unscramble_image(decoded_arr, password)

    return Image.fromarray(decoded_arr.astype('uint8'))
