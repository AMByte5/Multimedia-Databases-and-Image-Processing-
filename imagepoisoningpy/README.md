# Python project — Java-style layout

main.py contains the four attack switches, input path, epsilon, iterations and YOLO settings. Edit these values as in Java Main.java. Each attack lives in its own class file under operations/ and exposes poisonImage(inputPath, outputPath, differencePath). AttackImageUtils.py handles image loading and saving; _optimization.py shares the numerical search helpers; YoloScorer.py reads predictions.

Attacks: AdversarialPatchAttack (the only algorithm ported from Java), SPSAAttack, NESAttack and FourierSearchAttack. The checkerboard is an unoptimized visible baseline; the other three use YOLO feedback. Each starts from the original image.

Run in PowerShell:

```powershell
& "C:\Users\LapTop 1\OneDrive\Desktop\Yolo\venv\Scripts\python.exe" "C:\Users\LapTop 1\OneDrive\Desktop\imagepoisoningpy\main.py" "C:\path\image.jpg"
```

Or set input in main.py and run without arguments. Configuration is now in main.py, replacing the previous command-line options. Existing Java and YOLO files are unchanged.

Files save beside the input as py_image_AttackName.png and py_image_AttackName_difference.png. Difference pixels use min(255, abs(original-modified)*25), matching Java. Repeated runs overwrite the same result filenames. Extra detected PNGs and a JSON report show before/after YOLO results.

This evaluates inference-time evasion, not training-data poisoning. Success is not guaranteed. Scores take the maximum post-NMS confidence for the selected class or all classes. Zero only means no selected detections at the chosen threshold. Python search attacks respect epsilon; the Java checkerboard baseline does not. No ground-truth mAP evaluation is performed.

API reference: https://docs.ultralytics.com/modes/predict/


## Stronger confidence target
The four enabled attacks are now AdversarialPatch, SPSA, NES and MomentumAttack. MomentumAttack replaces FourierSearch in main; its old module remains available. MomentumAttack uses input gradients from an independent in-memory copy of YOLOv8, momentum, periodic restarts, and checks the quantized candidate with normal YOLO inference every iteration. Weights on disk are never changed.

The score now means the maximum selected detection confidence, not a sum. Main sets targetConfidence=0.55 and epsilon=32 (maximum RGB change; visible changes are possible). Reports mark below_target only when the baseline was at least 0.55 and the saved image scores strictly below it. The detection threshold remains 0.01; it is not raised to hide detections. The Java checkerboard remains unchanged and is not bounded by epsilon. The optimizer saves each improvement and stops below the target or after the iteration budget. Meeting the target is not guaranteed on other images.
