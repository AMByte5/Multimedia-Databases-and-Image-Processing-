"""Independent preprocessing defenses; Java-style switches and separate classes."""
import argparse
import json
import os
from pathlib import Path
import traceback

from operations.DefenseImageUtils import DefenseImageUtils
from operations.MedianDefense import MedianDefense
from operations.GaussianDefense import GaussianDefense
from operations.JpegDefense import JpegDefense
from operations.BitDepthDefense import BitDepthDefense
from operations.AutoDefense import AutoDefense


def main():
    useMedianDefense = True
    useGaussianDefense = True
    useJpegDefense = True
    useBitDepthDefense = True
    desktop = Path.home() / 'OneDrive' / 'Desktop'
    inputImage = desktop / 'iiiiii' / 'py_image10_MomentumAttack.png'
    weights = desktop / 'Yolo' / 'yolov8n.pt'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', nargs='?', default=str(inputImage), help='Raw attacked image, not a detection overlay')
    parser.add_argument('--clean', help='Optional original image for a matched-box comparison')
    parser.add_argument('--weights', default=str(weights))
    parser.add_argument('--output-dir', help='Default: defended/ beside the input')
    parser.add_argument('--no-yolo', action='store_true', help='Save defenses without model evaluation')
    parser.add_argument('--all-defenses', action='store_true', help='Optional comparison mode; default automatically selects one defense')
    args = parser.parse_args()
    source = Path(args.input).resolve()
    original = DefenseImageUtils.loadImage(source)
    folder = Path(args.output_dir).resolve() if args.output_dir else source.parent / 'defended'
    folder.mkdir(parents=True, exist_ok=True)
    scorer = None
    clean = None
    cleanPath = Path(args.clean) if args.clean else AutoDefense.findClean(source, original)
    if cleanPath:
        clean = DefenseImageUtils.loadImage(cleanPath)
        if clean.shape != original.shape:
            raise ValueError('Clean and attacked images must have identical dimensions.')
    if not args.no_yolo:
        if not Path(args.weights).is_file():
            raise FileNotFoundError(f'Local YOLO weights missing: {args.weights}')
        config = Path(__file__).resolve().parent / '.ultralytics'
        config.mkdir(exist_ok=True)
        os.environ['YOLO_CONFIG_DIR'] = str(config)
        import torch
        torch.set_num_threads(min(4, torch.get_num_threads()))
        from ultralytics import YOLO
        from YoloScorer import YoloScorer
        scorer = YoloScorer(YOLO(args.weights), 0.01, 640, None, 'cpu')

    selectedDefense, routing = AutoDefense.select(source, original, clean)
    print(f'Attack tag: {routing["attack_tag"]} ({routing["identification_method"]}); defense: {routing["selected_defense"]}')
    report = {'input': str(source), 'clean': str(cleanPath) if cleanPath else None, 'weights': args.weights,
              'automatic_routing': routing,
              'settings': {'confidence': 0.01, 'imgsz': 640, 'device': 'cpu'},
              'note': 'Confidence is not accuracy. Matched scores require same class and IoU >= 0.5 against clean detections. Preprocessing is not guaranteed protection.',
              'defenses': {}}
    reference = scorer.predict(clean)[1] if scorer and clean is not None else None

    def evaluate(rgb, prefix):
        if scorer is None:
            return {}
        score, detections, result = scorer.predict(rgb)
        result.save(filename=str(folder / f'{prefix}_detected.png'))
        data = {'max_confidence': score, 'detections': detections}
        if reference is not None:
            data['clean_box_matches'] = [
                {'class_id': ref['class_id'], 'name': ref['name'],
                 'reference_xyxy': ref['xyxy'], 'clean_confidence': ref['confidence'],
                 'matched_confidence': max((d['confidence'] for d in detections
                    if d['class_id'] == ref['class_id'] and iou(d['xyxy'], ref['xyxy']) >= 0.5), default=0.0)}
                for ref in reference]
        return data

    stem = f'def_py_{source.stem.removeprefix("py_")}'
    report['before'] = evaluate(original, f'{stem}_before')
    if clean is not None:
        report['clean_baseline'] = evaluate(clean, f'{stem}_clean')
    defenses = [
        (useMedianDefense, 'MedianDefense', MedianDefense(3)),
        (useGaussianDefense, 'GaussianDefense', GaussianDefense(1.0)),
        (useJpegDefense, 'JpegDefense', JpegDefense(75)),
        (useBitDepthDefense, 'BitDepthDefense', BitDepthDefense(5)),
    ]
    if not args.all_defenses:
        defenses = [(True, type(selectedDefense).__name__, selectedDefense)]
    failures = 0
    for enabled, name, defense in defenses:
        if not enabled:
            continue
        try:
            output = folder / f'{stem}_{name}.png'
            difference = folder / f'{stem}_{name}_difference.png'
            defense.defendImage(source, output, difference)
            # Evaluate pixels reloaded from the actual saved file.
            metrics = evaluate(DefenseImageUtils.loadImage(output), f'{stem}_{name}')
            metrics.update(output=str(output), difference=str(difference))
            if clean is not None:
                metrics['clean_after_defense'] = evaluate(defense.apply(clean), f'{stem}_{name}_clean')
            report['defenses'][name] = metrics
            print(f'{name}: saved {output.name}; max confidence={metrics.get("max_confidence", "not evaluated")}')
        except Exception as error:
            failures += 1
            traceback.print_exc()
            report['defenses'][name] = {'error': str(error)}
    reportPath = folder / f'{stem}_defense_report.json'
    reportPath.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(f'Report: {reportPath}')
    if failures:
        raise SystemExit(1)


def iou(a, b):
    intersection = max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))
    area = lambda box: max(0, box[2] - box[0]) * max(0, box[3] - box[1])
    union = area(a) + area(b) - intersection
    return intersection / union if union else 0.0


if __name__ == '__main__':
    main()
