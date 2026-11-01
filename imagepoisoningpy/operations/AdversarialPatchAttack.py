import numpy as np
from .AttackImageUtils import AttackImageUtils

def _apply(original):
    """Exact pattern/positions from Java AdversarialPatchAttack, not learned."""
    image = original.copy()
    height, width = image.shape[:2]
    size = max(1, int(min(width, height) * 0.12 + 0.5))
    cell = max(1, size // 8)
    yy, xx = np.indices((size, size))
    checker = ((xx // cell + yy // cell) % 2 == 0)
    patch = np.where(checker[..., None], [255, 0, 255], [0, 255, 0]).astype(np.uint8)
    for cx, cy in [(width // 2, height // 2), (width // 2, height // 4),
                   (width // 2, 3 * height // 4), (width // 4, height // 2),
                   (3 * width // 4, height // 2)]:
        x = max(0, min(cx - size // 2, width - size))
        y = max(0, min(cy - size // 2, height - size))
        image[y:y + size, x:x + size] = patch
    return image


class AdversarialPatchAttack:
    """Checkerboard baseline ported from the existing Java attack."""
    def __init__(self, epsilon, iterations):
        self.epsilon = epsilon
        self.iterations = iterations

    def poisonImage(self, inputPath, outputPath, differencePath):
        original = AttackImageUtils.loadImage(inputPath)
        modified = _apply(original)
        AttackImageUtils.saveResults(original, modified, outputPath, differencePath)
        return modified, 0
