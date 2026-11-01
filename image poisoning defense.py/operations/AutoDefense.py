import re
import numpy as np
from PIL import Image, ImageFilter
from .PatchDefense import PatchDefense, patch_mask
from .JpegDefense import JpegDefense
from .MedianDefense import MedianDefense


class AutoDefense:
    @staticmethod
    def select(path, rgb, clean=None):
        tokens = re.sub(r'[^a-z0-9]', '', path.stem.lower())
        known = ('AdversarialPatch', 'MomentumAttack', 'SPSAAttack', 'NESAttack',
                 'FourierSearchAttack', 'PGDAttack', 'SimBAAttack', 'SquareAttack')
        names = [name for name in known if name.lower() in tokens]
        evidence = {'patch_color_fraction': float(np.mean(patch_mask(rgb) > 0))}
        if len(names) == 1:
            tag = names[0]
            method = 'filename'
            certainty = 'filename label; not independently verified'
        else:
            method = 'image_heuristic'
            certainty = 'estimated category; exact attack algorithm cannot be identified reliably from pixels'
            if evidence['patch_color_fraction'] > 0.005:
                tag = 'CheckerboardPatchLike'
            elif clean is not None:
                delta = rgb.astype(np.float32) - clean.astype(np.float32)
                magnitude = np.max(np.abs(delta), axis=2)
                changed = magnitude > 2
                fraction = float(np.mean(changed))
                evidence.update(changed_fraction=fraction, mean_absolute_change=float(np.mean(np.abs(delta))))
                if fraction < 0.001:
                    tag = 'UnknownOrUnchanged'
                elif fraction < 0.05:
                    tag = 'SparseNoiseLike'
                else:
                    tag = 'DistributedPerturbationLike'
            else:
                small = Image.fromarray(rgb)
                smooth = np.array(small.filter(ImageFilter.MedianFilter(3))).astype(np.float32)
                evidence['median_residual'] = float(np.mean(np.abs(rgb.astype(np.float32) - smooth)))
                tag = 'NoiseLike' if evidence['median_residual'] > 8 else 'Unknown'
        if tag in ('AdversarialPatch', 'CheckerboardPatchLike'):
            defense = PatchDefense()
            reason = 'Mask the known checkerboard colors and inpaint their locations.'
        elif tag == 'SparseNoiseLike':
            defense = MedianDefense(3)
            reason = 'Median filtering selected for sparse pixel changes.'
        else:
            defense = JpegDefense(75)
            reason = 'JPEG preprocessing selected for distributed noise or as a conservative fixed fallback; it performed best on the local noise-attack examples.'
        return defense, {'attack_tag': tag, 'identification_method': method,
                         'certainty': certainty, 'selected_defense': type(defense).__name__,
                         'reason': reason, 'evidence': evidence,
                         'filename_ambiguous': len(names) > 1}

    @staticmethod
    def findClean(path, rgb):
        # Only an exact, unique base-name match; never guess another scene.
        stem = re.sub(r'^py_', '', path.stem, flags=re.I)
        stem = re.sub(r'_(AdversarialPatch|MomentumAttack|SPSAAttack|NESAttack|FourierSearchAttack|PGDAttack|SimBAAttack|SquareAttack)$', '', stem, flags=re.I)
        if stem == path.stem:
            return None
        candidates = [p for p in path.parent.iterdir() if p.is_file() and p != path
                      and p.stem.lower() == stem.lower() and p.suffix.lower() in ('.jpg', '.jpeg', '.png')]
        if len(candidates) != 1:
            return None
        return candidates[0]
