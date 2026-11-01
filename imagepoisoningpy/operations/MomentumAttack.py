"""Gradient-based confidence suppression for local Ultralytics YOLOv8 weights."""
import copy
import numpy as np
import torch
import torch.nn.functional as F
from .AttackImageUtils import AttackImageUtils


class MomentumAttack:
    def __init__(self, epsilon, iterations, scorer, seed=42, target=0.55):
        self.epsilon, self.iterations = epsilon, iterations
        self.scorer, self.seed, self.target = scorer, seed, target

    def poisonImage(self, inputPath, outputPath, differencePath):
        original = AttackImageUtils.loadImage(inputPath)
        best = original.copy()
        best_score = self.scorer(best)
        queries = 1
        # Independent in-memory copy: no training or changes to the weights file.
        net = copy.deepcopy(self.scorer.model.model).float().eval()
        device = next(net.parameters()).device
        for parameter in net.parameters():
            parameter.requires_grad_(False)
        base = torch.from_numpy(original.copy()).permute(2, 0, 1)[None].to(device).float() / 255
        eps = self.epsilon / 255
        lower, upper = (base - eps).clamp(0, 1), (base + eps).clamp(0, 1)
        height, width = original.shape[:2]
        size = int(self.scorer.imgsz)
        ratio = min(size / height, size / width)
        nh, nw = round(height * ratio), round(width * ratio)
        stride = int(net.stride.max().item())
        # Match predict's rectangular auto-letterbox size.
        dh, dw = (size - nh) % stride, (size - nw) % stride
        padding = (round(dw / 2 - .1), round(dw / 2 + .1),
                   round(dh / 2 - .1), round(dh / 2 + .1))
        generator = torch.Generator(device=device).manual_seed(self.seed)
        x = base.clone()
        momentum = torch.zeros_like(x)
        gradients = 0
        for iteration in range(self.iterations):
            if best_score < self.target:
                break
            # Restart at the best quantized candidate periodically.
            if iteration and iteration % 30 == 0:
                anchor = torch.from_numpy(best.copy()).permute(2, 0, 1)[None].to(device).float() / 255
                noise = (torch.rand(base.shape, device=device, generator=generator) - .5) * eps / 2
                x = torch.maximum(lower, torch.minimum(upper, anchor + noise))
                momentum.zero_()
            x = x.detach().requires_grad_(True)
            resized = F.interpolate(x, size=(nh, nw), mode="bilinear", align_corners=False)
            prediction = net(F.pad(resized, padding, value=114 / 255))
            prediction = prediction[0] if isinstance(prediction, tuple) else prediction
            nc = len(self.scorer.model.names)
            if not isinstance(prediction, torch.Tensor) or prediction.ndim != 3 or prediction.shape[1] != nc + 4:
                raise ValueError("MomentumAttack requires YOLOv8 decoded [B,4+classes,anchors] predictions")
            confidence = prediction[:, 4:, :]
            if self.scorer.class_id is not None:
                confidence = confidence[:, self.scorer.class_id:self.scorer.class_id + 1, :]
            values = confidence.flatten()
            top = values.topk(min(20, values.numel())).values
            loss = top.max() + top.mean()
            gradient, = torch.autograd.grad(loss, x)
            gradients += 1
            if not torch.isfinite(gradient).all():
                raise RuntimeError("Non-finite image gradient")
            momentum = .9 * momentum + gradient / gradient.abs().mean().clamp_min(1e-12)
            step = (2.0 if iteration < self.iterations * .7 else 1.0) / 255
            x = torch.maximum(lower, torch.minimum(upper, x.detach() - step * momentum.sign()))
            candidate = (x[0].detach().permute(1, 2, 0).cpu().numpy() * 255).round().clip(0, 255).astype(np.uint8)
            value = self.scorer(candidate)
            queries += 1
            if value < best_score:
                best, best_score = candidate.copy(), value
                # Save improvements immediately, including interrupted runs.
                AttackImageUtils.saveResults(original, best, outputPath, differencePath)
            print(f"MomentumAttack {iteration + 1}/{self.iterations}: best confidence={best_score:.2%}, target < {self.target:.0%}", flush=True)
        self.gradient_steps = gradients
        AttackImageUtils.saveResults(original, best, outputPath, differencePath)
        return best, queries
