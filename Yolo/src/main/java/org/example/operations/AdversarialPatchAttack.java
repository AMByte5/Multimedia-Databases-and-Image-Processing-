
package org.example.operations;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public class AdversarialPatchAttack {

    private final int epsilon;
    private final int iterations;
    private double patchFraction = 0.12;

    public AdversarialPatchAttack(int epsilon, int iterations) {
        this.epsilon = epsilon;
        this.iterations = iterations;
    }

    public void setPatchFraction(double fraction) {
        if (fraction <= 0 || fraction > 0.25) {
            throw new IllegalArgumentException(
                    "Patch fraction must be between 0 and 0.25"
            );
        }
        this.patchFraction = fraction;
    }

    public void poisonImage(
            String inputPath,
            String outputPath,
            String differencePath
    ) throws IOException {

        BufferedImage original =
                AttackImageUtils.loadImage(inputPath);

        BufferedImage patched =
                AttackImageUtils.copyImage(original);

        int width = original.getWidth();
        int height = original.getHeight();

        int size = Math.max(
                1,
                (int) Math.round(
                        Math.min(width, height) * patchFraction
                )
        );

        int[][] positions = {
                {width / 2, height / 2},
                {width / 2, height / 4},
                {width / 2, 3 * height / 4},
                {width / 4, height / 2},
                {3 * width / 4, height / 2}
        };

        for (int[] position : positions) {

            int x = Math.max(
                    0,
                    Math.min(position[0] - size / 2, width - size)
            );

            int y = Math.max(
                    0,
                    Math.min(position[1] - size / 2, height - size)
            );

            applyPatch(patched, x, y, size);
        }

        AttackImageUtils.saveResults(
                original,
                patched,
                outputPath,
                differencePath
        );

        System.out.println("Adversarial Patch completed.");
    }

    private void applyPatch(
            BufferedImage image,
            int startX,
            int startY,
            int size
    ) {

        int cellSize = Math.max(1, size / 8);

        for (int y = 0; y < size; y++) {
            for (int x = 0; x < size; x++) {

                boolean checker =
                        ((x / cellSize) + (y / cellSize)) % 2 == 0;

                int r = checker ? 255 : 0;
                int g = checker ? 0 : 255;
                int b = checker ? 255 : 0;

                image.setRGB(
                        startX + x,
                        startY + y,
                        AttackImageUtils.rgb(r, g, b)
                );
            }
        }
    }
}
