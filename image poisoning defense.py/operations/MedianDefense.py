import numpy as np
from PIL import Image, ImageFilter
from .DefenseImageUtils import ImageDefense


class MedianDefense(ImageDefense):
    def __init__(self, size=3):
        if size < 3 or size % 2 == 0:
            raise ValueError('Median size must be odd and at least 3.')
        self.size = size

    def apply(self, rgb):
        return np.array(Image.fromarray(rgb).filter(ImageFilter.MedianFilter(self.size)))
