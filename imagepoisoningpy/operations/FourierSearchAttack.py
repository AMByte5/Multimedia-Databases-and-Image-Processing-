from .AttackImageUtils import AttackImageUtils
from ._optimization import optimize


class FourierSearchAttack:
    def __init__(self, epsilon, iterations, scorer, seed=42):
        if not 0 <= epsilon <= 255 or iterations < 0:
            raise ValueError("Invalid epsilon or iterations")
        self.epsilon = epsilon
        self.iterations = iterations
        self.scorer = scorer
        self.seed = seed

    def poisonImage(self, inputPath, outputPath, differencePath):
        original = AttackImageUtils.loadImage(inputPath)
        modified, queries = optimize(original, self.scorer, "FourierSearchAttack",
                                     self.epsilon, self.iterations, self.seed)
        AttackImageUtils.saveResults(original, modified, outputPath, differencePath)
        return modified, queries
