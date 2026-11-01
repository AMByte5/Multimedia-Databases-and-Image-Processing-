from pathlib import Path
import numpy as np
from PIL import Image


class AttackImageUtils:
    @staticmethod
    def loadImage(path):
        with Image.open(path) as image:
            return np.asarray(image.convert("RGB")).copy()

    @staticmethod
    def saveResults(original, modified, outputPath, differencePath):
        for path in (outputPath, differencePath):
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(modified).save(outputPath, format="PNG")
        delta = np.abs(original.astype(np.int16) - modified.astype(np.int16))
        difference = np.clip(delta * 25, 0, 255).astype(np.uint8)
        Image.fromarray(difference).save(differencePath, format="PNG")
        print(f"Saved: {outputPath}\nSaved: {differencePath}", flush=True)
