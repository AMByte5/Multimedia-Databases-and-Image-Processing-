import numpy as np
from PIL import Image, ImageFilter
from .DefenseImageUtils import ImageDefense


class GaussianDefense(ImageDefense):
    def __init__(self, radius=1.0):
        if radius <= 0:
            raise ValueError('Gaussian radius must be positive.')
        self.radius = radius

    def apply(self, rgb):
        return np.array(Image.fromarray(rgb).filter(ImageFilter.GaussianBlur(self.radius)))
