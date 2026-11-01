"""Java-style configuration and four independent attack classes."""
import json
import os
import sys
import traceback
from pathlib import Path

from operations.AdversarialPatchAttack import AdversarialPatchAttack
from operations.SPSAAttack import SPSAAttack
from operations.NESAttack import NESAttack
from operations.MomentumAttack import MomentumAttack
from operations.AttackImageUtils import AttackImageUtils
from YoloScorer import YoloScorer


def main():

    useAdversarialPatch = True
    useSPSAAttack = True
    useNESAttack = True
    useMomentumAttack = True

    # =====================================
    # INPUT IMAGE — edit this path, or pass it on the command line
    # =====================================
    input = r"C:\Users\LapTop 1\OneDrive\Desktop\iiiiii\image10.jpg"
    if len(sys.argv) > 1:
        input = sys.argv[1]

    # =====================================
    # ATTACK PARAMETERS
    # =====================================
    epsilon = 32  # RGB bound for Python attacks; stronger changes may be visible
    iterations = 100
    seed = 42
    targetConfidence = 0.55
    weights = r"C:\Users\LapTop 1\OneDrive\Desktop\Yolo\yolov8n.pt"
    confidence = 0.01
    imageSize = 640
    classId = None  # None suppresses all classes; set an integer for one class
    device = "cpu"

    inputFile = Path(input)
    imageName = inputFile.stem
    folder = inputFile.parent
    if not inputFile.is_file():
        raise FileNotFoundError(f"Set input to an existing image: {input}")
    enabled = [
        (useAdversarialPatch, "AdversarialPatch", AdversarialPatchAttack),
        (useMomentumAttack, "MomentumAttack", MomentumAttack),
        (useSPSAAttack, "SPSAAttack", SPSAAttack),
        (useNESAttack, "NESAttack", NESAttack),
    ]
    if not any(flag for flag, _, _ in enabled):
        print("No attacks enabled.")
        return
    if not Path(weights).is_file():
        raise FileNotFoundError(f"Local YOLO weights not found: {weights}")
    config = Path(__file__).resolve().parent / ".ultralytics"
    config.mkdir(exist_ok=True)
    os.environ["YOLO_CONFIG_DIR"] = str(config)
    import torch
    torch.set_num_threads(min(4, torch.get_num_threads()))
    from ultralytics import YOLO
    scorer = YoloScorer(YOLO(weights), confidence, imageSize, classId, device)
    original = AttackImageUtils.loadImage(input)
    baseline, detections, result = scorer.predict(original)
    if baseline == 0:
        print("No baseline detections for the selected class/threshold; suppression cannot be measured.")
    result.save(filename=str(folder / f"py_{imageName}_original_detected.png"))
    report = {"original_score": baseline, "original_detections": detections,
              "settings": {"input": str(inputFile.resolve()), "weights": weights,
                           "epsilon": epsilon, "iterations": iterations, "seed": seed,
                           "confidence": confidence, "imgsz": imageSize,
                           "class_id": classId, "device": device,
                           "metric": "maximum_selected_detection_confidence",
                           "target_confidence": targetConfidence}, "attacks": {}}

    # =====================================
    # RUN ATTACKS — each loads the original image, as in Java
    # =====================================
    failures = 0
    for useAttack, attackName, AttackClass in enabled:
        if not useAttack:
            continue
        try:
            poisoned = folder / f"py_{imageName}_{attackName}.png"
            difference = folder / f"py_{imageName}_{attackName}_difference.png"
            if AttackClass is AdversarialPatchAttack:
                attack = AttackClass(epsilon, iterations)
            else:
                attack = AttackClass(epsilon, iterations, scorer, seed)
                if isinstance(attack, MomentumAttack):
                    attack.target = targetConfidence
            _, queries = attack.poisonImage(input, poisoned, difference)
            score, found, result = scorer.predict(AttackImageUtils.loadImage(poisoned))
            result.save(filename=str(folder / f"py_{imageName}_{attackName}_detected.png"))
            report["attacks"][attackName] = {
                "output": str(poisoned), "difference": str(difference),
                "score": score, "score_reduction": baseline - score,
                "below_target": baseline >= targetConfidence and score < targetConfidence,
                "target_confidence": targetConfidence,
                "gradient_steps": getattr(attack, "gradient_steps", 0),
                "suppressed_at_threshold": baseline > 0 and score == 0,
                "detections": found, "optimization_queries": queries,
            }
            print(f"{attackName}: original={baseline:.6f}, modified={score:.6f}")
        except Exception as error:
            failures += 1
            traceback.print_exc()
            report["attacks"][attackName] = {"error": str(error)}
        (folder / f"py_{imageName}_attack_report.json").write_text(
            json.dumps(report, indent=2), encoding="utf-8")
    successful = [name for name, data in report["attacks"].items() if data.get("below_target")]
    print(f"Attacks below {targetConfidence:.0%}: {successful}" if successful else
          f"Target below {targetConfidence:.0%} not achieved by any attack; see report.")
    print("Finished running enabled attacks.")
    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
