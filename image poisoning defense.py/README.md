# Image poisoning defense

## Automatic mode (default)

Provide only the image path. No attack type or defense type is needed. For example `py_image10_MomentumAttack.png` routes automatically to JPEG defense. Filename matching ignores case and punctuation. Recognized labels: AdversarialPatch, MomentumAttack, SPSAAttack, NESAttack, FourierSearchAttack, PGDAttack, SimBAAttack, and SquareAttack.

Checkerboard patches route to PatchDefense, which masks the project's magenta/green pattern and inpaints it. Other named attacks route to JPEG quality 75, based on the local comparison results, rather than claiming each attack has a unique inverse. Patch inpainting needs OpenCV, already included in the existing YOLO environment. It estimates missing content; it cannot recover hidden original pixels.

Without a recognized name, image heuristics tag checkerboard-patch-like, noise-like, or unknown content. An optional clean reference allows sparse versus distributed change estimates. These are estimated categories, not reliable identification of the exact attack algorithm; natural textures/colors can cause false positives. Unknown images use the fixed JPEG fallback. The JSON report records the tag, its source, evidence, uncertainty, and selected defense. Filename tags are labels, not verified evidence of the attack.

For a known attack filename, the program automatically finds a unique matching original beside it (e.g. `image10.jpg`). `--clean` remains an optional override for evaluation, never a required attack/defense selection. Use `--all-defenses` only to compare the original four defenses; normal mode applies one automatically selected defense.

Separate defense project for the existing YOLO adversarial-image attacks. The folder is named `image poisoning defense.py` as requested; run `main.py` inside it. These are inference-time preprocessing defenses, not training-data cleanup or retraining.

Same organization as the attacks: switches and parameters in `main.py`, four independent classes in `operations/`, shared `DefenseImageUtils`, and a local `YoloScorer` helper. Each defense starts from the same attacked image, not the output of another defense.

- MedianDefense: 3 x 3 median filter for local noise.
- GaussianDefense: radius 1 smoothing for high-frequency noise.
- JpegDefense: JPEG quality 75 compression, then lossless PNG output.
- BitDepthDefense: quantize each color channel to 5 bits.

Use the existing YOLO Python environment (it already contains the dependencies):

```powershell
& "$env:USERPROFILE\OneDrive\Desktop\Yolo\venv\Scripts\python.exe" "$env:USERPROFILE\OneDrive\Desktop\image poisoning defense.py\main.py"
```

Optional arguments after main.py: `"path\attacked.png" --clean "path\original.jpg" --output-dir "path\results"`. Use `--no-yolo` to process without evaluating. Change the four switches or constructor parameters in main.py as needed.

Outputs go to `defended/` beside the input by default. Each defense saves `def_py_<input>_<DefenseName>.png`, a 25x amplified absolute difference image relative to the attacked input, and a YOLO detection overlay. The JSON report contains before/after detections. Input files and model weights are never overwritten.

For fair evaluation, provide `--clean`. The report compares same-class boxes at IoU >= 0.5 against clean detections, and also measures each defense on the clean image. A higher maximum confidence alone does not demonstrate recovery or improved accuracy. Clean detections are a reference, not human ground truth. Dataset accuracy requires labeled data.

These transformations may remove small perturbations, but can damage image details and may fail against patches, low-frequency changes, or adaptive attacks. A patch hides image information that ordinary filtering cannot reconstruct. No guaranteed defense or automatic best-defense selection is claimed.
