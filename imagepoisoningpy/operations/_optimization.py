import numpy as np


def project(candidate, original, epsilon):
    base = original.astype(np.float32)
    return np.rint(np.clip(candidate, np.maximum(0, base - epsilon),
                           np.minimum(255, base + epsilon))).astype(np.uint8)


def expand_grid(grid, height, width):
    # Nearest-neighbor expansion keeps search dimension small without interpolation artifacts.
    y = np.minimum(np.arange(height) * grid.shape[0] // height, grid.shape[0] - 1)
    x = np.minimum(np.arange(width) * grid.shape[1] // width, grid.shape[1] - 1)
    return grid[y[:, None], x[None, :]]


def optimize(original, score, method, epsilon, iterations, seed, grid_size=16):
    """SPSA and NES estimate a gradient; Fourier search accepts improving proposals.

    These use thresholded post-NMS YOLO scores, so plateaus are possible. They
    attempt to suppress detections, with no promise of success or transferability.
    """
    rng = np.random.default_rng(seed)
    height, width = original.shape[:2]
    shape = (min(grid_size, height), min(grid_size, width), 3)
    best = original.copy()
    best_score = score(best)
    base = original.astype(np.float32)
    latent = np.zeros(shape, dtype=np.float32)
    queries = 1
    sigma = max(1.0, epsilon / 4)
    step = max(1.0, epsilon / 8)
    yy, xx = np.mgrid[0:height, 0:width]
    for iteration in range(iterations):
        if best_score == 0 or epsilon == 0:
            break
        if method == "FourierSearchAttack":
            fx, fy = rng.integers(0, 9, size=2)
            wave = np.cos(2 * np.pi * (fx * xx / width + fy * yy / height)
                          + rng.uniform(0, 2 * np.pi))
            direction = wave[..., None] * rng.choice([-1, 1], size=3)
            candidate = project(best.astype(np.float32) + step * direction, original, epsilon)
        else:
            direction = (rng.choice([-1., 1.], size=shape) if method == "SPSAAttack"
                         else rng.normal(size=shape)).astype(np.float32)
            plus = project(base + expand_grid(np.clip(latent + sigma * direction,
                           -epsilon, epsilon), height, width), original, epsilon)
            minus = project(base + expand_grid(np.clip(latent - sigma * direction,
                            -epsilon, epsilon), height, width), original, epsilon)
            positive, negative = score(plus), score(minus)
            queries += 2
            # Preserve every improvement, including finite-difference probes.
            for probe, value in [(plus, positive), (minus, negative)]:
                if value < best_score:
                    best, best_score = probe.copy(), value
            gradient = (positive - negative) / (2 * sigma) * direction
            latent = np.clip(latent - step * np.sign(gradient), -epsilon, epsilon)
            candidate = project(base + expand_grid(latent, height, width), original, epsilon)
        value = score(candidate)
        queries += 1
        if value < best_score:
            best, best_score = candidate.copy(), value
        if (iteration + 1) % 10 == 0:
            print(f"{method}: {iteration + 1}/{iterations}, score={best_score:.6f}", flush=True)
    return best, queries
