from io import BytesIO
import numpy as np
from PIL import Image
from .DefenseImageUtils import ImageDefense


class JpegDefense(ImageDefense):
    def __init__(self, quality=75):
        if not 1 <= quality <= 95:
            raise ValueError('JPEG quality must be between 1 and 95.')
        self.quality = quality

    def apply(self, rgb):
        buffer = BytesIO()
        Image.fromarray(rgb).save(buffer, format='JPEG', quality=self.quality)
        buffer.seek(0)
        with Image.open(buffer) as image:
            return np.array(image.convert('RGB'))
