import numpy as np
from .DefenseImageUtils import ImageDefense


class BitDepthDefense(ImageDefense):
    def __init__(self, bits=5):
        if not 1 <= bits <= 8:
            raise ValueError('Bit depth must be between 1 and 8.')
        self.bits = bits

    def apply(self, rgb):
        levels = 2 ** self.bits - 1
        return np.rint(np.rint(rgb.astype(np.float32) / 255 * levels) / levels * 255).astype(np.uint8)
