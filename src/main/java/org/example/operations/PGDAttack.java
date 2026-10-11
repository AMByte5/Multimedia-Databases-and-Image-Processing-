
package org.example.operations;

import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.Random;

public class PGDAttack {

    private final int epsilon;
    private final int iterations;
    private final Random random = new Random(42);

    public PGDAttack(int epsilon, int iterations) {

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

        int alpha = Math.max(1, epsilon / 4);

        // Initial bounded random perturbation
        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {

                int originalRGB = original.getRGB(x, y);

                int r = (originalRGB >> 16) & 255;
                int g = (originalRGB >> 8) & 255;
                int b = originalRGB & 255;

                poisoned.setRGB(
                        x,
                        y,
                        AttackImageUtils.rgb(
                                AttackImageUtils.clamp(r + randomDelta()),
                                AttackImageUtils.clamp(g + randomDelta()),
                                AttackImageUtils.clamp(b + randomDelta())
                        )
                );
            }
        }

        // Cap full-image iterations for performance
        int effectiveIterations = Math.min(iterations, 20);

        for (int i = 0; i < effectiveIterations; i++) {

            for (int y = 0; y < height; y++) {
                for (int x = 0; x < width; x++) {

                    int originalRGB = original.getRGB(x, y);
                    int currentRGB = poisoned.getRGB(x, y);

                    int originalR = (originalRGB >> 16) & 255;
                    int originalG = (originalRGB >> 8) & 255;
                    int originalB = originalRGB & 255;

                    int currentR = (currentRGB >> 16) & 255;
                    int currentG = (currentRGB >> 8) & 255;
                    int currentB = currentRGB & 255;

                    int newR = project(
                            currentR + randomSign() * alpha,
                            originalR
                    );

                    int newG = project(
                            currentG + randomSign() * alpha,
                            originalG
                    );

                    int newB = project(
                            currentB + randomSign() * alpha,
                            originalB
                    );

                    poisoned.setRGB(
                            x,
                            y,
                            AttackImageUtils.rgb(newR, newG, newB)
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
                "PGD-inspired bounded-noise baseline completed."
        );
    }

    private int randomDelta() {
        if (epsilon == 0) {
            return 0;
        }
        return random.nextInt(2 * epsilon + 1) - epsilon;
    }

    private int randomSign() {
        return random.nextBoolean() ? 1 : -1;
    }

    private int project(int candidate, int originalValue) {

        int lower = Math.max(0, originalValue - epsilon);
        int upper = Math.min(255, originalValue + epsilon);

        return Math.max(lower, Math.min(upper, candidate));
    }
}
