from pathlib import Path
import numpy as np
from PIL import Image, ImageOps


class DefenseImageUtils:
    @staticmethod
    def loadImage(path):
        with Image.open(path) as image:
            return np.array(ImageOps.exif_transpose(image).convert('RGB'))

    @staticmethod
    def saveResults(original, modified, outputPath, differencePath):
        for path in (outputPath, differencePath):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(modified).save(outputPath, format='PNG')
        delta = np.abs(original.astype(np.int16) - modified.astype(np.int16))
        Image.fromarray(np.clip(delta * 25, 0, 255).astype(np.uint8)).save(differencePath)


class ImageDefense:
    def defendImage(self, inputPath, outputPath, differencePath):
        original = DefenseImageUtils.loadImage(inputPath)
        modified = self.apply(original)
        DefenseImageUtils.saveResults(original, modified, outputPath, differencePath)
        return modified
