from PIL import Image, ImageEnhance, ImageChops
from skimage.filters import threshold_local
import numpy as np

def adjust_contrast_and_brightness(image, contrast_factor=1.5, brightness_factor=2):
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast_factor)
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness_factor)
    return image

def adaptive_thresholding(image):
    block_size = 35  # Define the size of the neighbourhood
    offset = 45
    adaptive_thresh = threshold_local(np.array(image), block_size, offset=offset)
    binary_adaptive = np.array(image) > adaptive_thresh
    return Image.fromarray((binary_adaptive * 255).astype(np.uint8))

def blend_images(original, edges, blend_factor=0.5):
    # Increase contrast of the original image
    enhancer = ImageEnhance.Contrast(original)
    high_contrast = enhancer.enhance(2.0)
    # Blend the high-contrast image with the edge image
    blended = ImageChops.blend(high_contrast, edges, blend_factor)
    return blended

def process_image(original_target):
    target = original_target.convert("L")
    target = adjust_contrast_and_brightness(target)
    target = adaptive_thresholding(target)

    return target