import numpy as np
from .DefenseImageUtils import ImageDefense


def patch_mask(rgb):
    # Signature of this project's magenta/green checkerboard patch.
    r, g, b = rgb.astype(np.int16).transpose(2, 0, 1)
    return (((r > 220) & (b > 220) & (g < 35)) |
            ((g > 220) & (r < 35) & (b < 35))).astype(np.uint8) * 255


class PatchDefense(ImageDefense):
    def apply(self, rgb):
        import cv2
        mask = patch_mask(rgb)
        count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
        filtered = np.zeros_like(mask)
        for index in range(1, count):
            if stats[index, cv2.CC_STAT_AREA] >= 4:
                filtered[labels == index] = 255
        filtered = cv2.dilate(filtered, np.ones((3, 3), np.uint8))
        return cv2.inpaint(rgb, filtered, 3, cv2.INPAINT_TELEA)
