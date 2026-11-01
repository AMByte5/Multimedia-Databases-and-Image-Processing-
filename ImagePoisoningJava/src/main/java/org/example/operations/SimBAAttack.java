
package org.example.operations;

import java.awt.image.BufferedImage;
import java.io.IOException;
import java.util.Random;

public class SimBAAttack {

    private final int epsilon;
    private final int iterations;
    private final Random random = new Random(42);

    // Radius 3 creates a 7x7 neighborhood
    private int radius = 3;

    public SimBAAttack(int epsilon, int iterations) {

        if (epsilon < 0 || epsilon > 255 || iterations < 0) {
            throw new IllegalArgumentException(
                    "Invalid epsilon or iterations"
            );
        }

        this.epsilon = epsilon;
        this.iterations = iterations;
    }

    public void setRadius(int radius) {
        if (radius < 0 || radius > 20) {
            throw new IllegalArgumentException(
                    "Radius must be between 0 and 20"
            );
        }
        this.radius = radius;
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

        for (int i = 0; i < iterations; i++) {

            int centerX = random.nextInt(width);
            int centerY = random.nextInt(height);

            int channel = random.nextInt(3);
            int direction = random.nextBoolean() ? 1 : -1;

            int startX = Math.max(0, centerX - radius);
            int endX = Math.min(width - 1, centerX + radius);

            int startY = Math.max(0, centerY - radius);
            int endY = Math.min(height - 1, centerY + radius);

            for (int y = startY; y <= endY; y++) {
                for (int x = startX; x <= endX; x++) {

                    int originalRGB = original.getRGB(x, y);

                    int r = (originalRGB >> 16) & 255;
                    int g = (originalRGB >> 8) & 255;
                    int b = originalRGB & 255;

                    int delta = direction * epsilon;

                    if (channel == 0) {
                        r = AttackImageUtils.clamp(r + delta);
                    } else if (channel == 1) {
                        g = AttackImageUtils.clamp(g + delta);
                    } else {
                        b = AttackImageUtils.clamp(b + delta);
                    }

                    poisoned.setRGB(
                            x,
                            y,
                            AttackImageUtils.rgb(r, g, b)
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
                "SimBA-inspired neighborhood perturbation completed."
        );
    }
}
