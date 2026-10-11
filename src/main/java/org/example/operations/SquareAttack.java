
package org.example.operations;

import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.Random;

public class SquareAttack {

    private final int epsilon;
    private final int iterations;
    private final Random random = new Random(42);

    public SquareAttack(int epsilon, int iterations) {

        if (epsilon < 0 || epsilon > 255 || iterations < 0) {
            throw new IllegalArgumentException(
                    "Invalid epsilon or iterations"
            );
        }

        this.epsilon = epsilon;
        this.iterations = iterations;
    }

    public void poisonImage(
            String inputPath,
            String outputPath,
            String differencePath
    ) throws IOException {

        BufferedImage original =
                AttackImageUtils.loadImage(inputPath);

        BufferedImage poisoned =
                AttackImageUtils.copyImage(original);

        int width = original.getWidth();
        int height = original.getHeight();

        int minDimension = Math.min(width, height);

        for (int i = 0; i < iterations; i++) {

            double progress = iterations == 0
                    ? 0
                    : (double) i / iterations;

            double fraction;

            if (progress < 0.25) {
                fraction = 0.25;
            } else if (progress < 0.50) {
                fraction = 0.15;
            } else if (progress < 0.75) {
                fraction = 0.08;
            } else {
                fraction = 0.04;
            }

            int size = Math.max(
                    1,
                    (int) (minDimension * fraction)
            );

            int startX = random.nextInt(width - size + 1);
            int startY = random.nextInt(height - size + 1);

            // Independent channel directions
            int deltaR = random.nextBoolean() ? epsilon : -epsilon;
            int deltaG = random.nextBoolean() ? epsilon : -epsilon;
            int deltaB = random.nextBoolean() ? epsilon : -epsilon;

            for (int y = startY; y < startY + size; y++) {
                for (int x = startX; x < startX + size; x++) {

                    int originalRGB = original.getRGB(x, y);

                    int r = (originalRGB >> 16) & 255;
                    int g = (originalRGB >> 8) & 255;
                    int b = originalRGB & 255;

                    poisoned.setRGB(
                            x,
                            y,
                            AttackImageUtils.rgb(
                                    AttackImageUtils.clamp(r + deltaR),
                                    AttackImageUtils.clamp(g + deltaG),
                                    AttackImageUtils.clamp(b + deltaB)
                            )
                    );
                }
            }
        }

        AttackImageUtils.saveResults(
                original,
                poisoned,
                outputPath,
                differencePath
        );

        System.out.println(
                "Square perturbation baseline completed."
        );
    }
}
