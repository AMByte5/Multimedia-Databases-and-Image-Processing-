package org.example.operations;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.Random;

public class Attack {

    private final int epsilon;
    private final int iterations;
    private final Random random;

    public Attack(int epsilon, int iterations) {
        this.epsilon = epsilon;
        this.iterations = iterations;
        this.random = new Random();
    }

    public void poisonImage(
            String inputPath,
            String outputPath,
            String differencePath
    ) throws IOException {

        BufferedImage original = ImageIO.read(new File(inputPath));

        if (original == null) {
            throw new IOException(
                    "Could not load image: " + inputPath
            );
        }

        int width = original.getWidth();
        int height = original.getHeight();

        BufferedImage poisoned = copyImage(original);

        System.out.println("==============================");
        System.out.println("JAVA ADVERSARIAL ATTACK");
        System.out.println("==============================");

        System.out.println("Width: " + width);
        System.out.println("Height: " + height);
        System.out.println("Epsilon: " + epsilon + "/255");
        System.out.println("Iterations: " + iterations);

        /*
         * Initial bounded perturbation.
         *
         * Every channel is still constrained to:
         *
         * original - epsilon
         *
         * through
         *
         * original + epsilon
         */
        initializePerturbation(
                original,
                poisoned
        );

        /*
         * Iterative square perturbations.
         *
         * Later this loop will use YOLO confidence
         * as its acceptance function.
         */
        for (int iteration = 0;
             iteration < iterations;
             iteration++) {

            double progress =
                    (double) iteration / iterations;

            int squareSize =
                    calculateSquareSize(
                            width,
                            height,
                            progress
                    );

            applySquare(
                    original,
                    poisoned,
                    squareSize
            );

            if (iteration % 100 == 0) {

                System.out.println(
                        "Iteration "
                                + iteration
                                + "/"
                                + iterations
                                + " | square="
                                + squareSize
                );
            }
        }

        /*
         * Verify that the final result has NOT
         * exceeded epsilon.
         */
        int maxDifference =
                calculateMaximumDifference(
                        original,
                        poisoned
                );

        long changedPixels =
                countChangedPixels(
                        original,
                        poisoned
                );

        System.out.println();
        System.out.println("Changed pixels: "
                + changedPixels);

        System.out.println(
                "Maximum channel difference: "
                        + maxDifference
        );

        if (maxDifference > epsilon) {

            throw new IllegalStateException(
                    "Attack exceeded epsilon!"
            );
        }

        saveImage(
                poisoned,
                outputPath
        );

        BufferedImage difference =
                createDifferenceImage(
                        original,
                        poisoned
                );

        saveImage(
                difference,
                differencePath
        );

        System.out.println();
        System.out.println("==============================");
        System.out.println("ATTACK COMPLETE");
        System.out.println("==============================");

        System.out.println(
                "Poisoned image:"
        );

        System.out.println(outputPath);

        System.out.println(
                "\nDifference map:"
        );

        System.out.println(differencePath);
    }


    private void initializePerturbation(
            BufferedImage original,
            BufferedImage poisoned
    ) {

        for (int y = 0;
             y < original.getHeight();
             y++) {

            for (int x = 0;
                 x < original.getWidth();
                 x++) {

                int rgb =
                        original.getRGB(x, y);

                int r = red(rgb);
                int g = green(rgb);
                int b = blue(rgb);

                r += random.nextBoolean()
                        ? epsilon
                        : -epsilon;

                g += random.nextBoolean()
                        ? epsilon
                        : -epsilon;

                b += random.nextBoolean()
                        ? epsilon
                        : -epsilon;

                r = clamp(r);
                g = clamp(g);
                b = clamp(b);

                poisoned.setRGB(
                        x,
                        y,
                        rgb(r, g, b)
                );
            }
        }
    }


    private void applySquare(
            BufferedImage original,
            BufferedImage poisoned,
            int squareSize
    ) {

        int width = original.getWidth();
        int height = original.getHeight();

        int maxX =
                Math.max(
                        1,
                        width - squareSize
                );

        int maxY =
                Math.max(
                        1,
                        height - squareSize
                );

        int startX =
                random.nextInt(maxX);

        int startY =
                random.nextInt(maxY);

        int direction =
                random.nextBoolean()
                        ? epsilon
                        : -epsilon;

        for (int y = startY;
             y < Math.min(
                     startY + squareSize,
                     height
             );
             y++) {

            for (int x = startX;
                 x < Math.min(
                         startX + squareSize,
                         width
                 );
                 x++) {

                int originalRGB =
                        original.getRGB(x, y);

                int originalR =
                        red(originalRGB);

                int originalG =
                        green(originalRGB);

                int originalB =
                        blue(originalRGB);

                /*
                 * Candidate values are constructed
                 * relative to the ORIGINAL image.
                 *
                 * This prevents perturbations from
                 * accumulating beyond epsilon.
                 */

                int newR =
                        clamp(
                                originalR
                                        + direction
                        );

                int newG =
                        clamp(
                                originalG
                                        + direction
                        );

                int newB =
                        clamp(
                                originalB
                                        + direction
                        );

                poisoned.setRGB(
                        x,
                        y,
                        rgb(
                                newR,
                                newG,
                                newB
                        )
                );
            }
        }
    }


    private int calculateSquareSize(
            int width,
            int height,
            double progress
    ) {

        int minDimension =
                Math.min(width, height);

        double percentage;

        if (progress < 0.10) {
            percentage = 0.20;

        } else if (progress < 0.30) {
            percentage = 0.10;

        } else if (progress < 0.60) {
            percentage = 0.05;

        } else if (progress < 0.80) {
            percentage = 0.025;

        } else {
            percentage = 0.01;
        }

        return Math.max(
                1,
                (int) (
                        minDimension
                                * percentage
                )
        );
    }


    private BufferedImage createDifferenceImage(
            BufferedImage original,
            BufferedImage poisoned
    ) {

        int width = original.getWidth();
        int height = original.getHeight();

        BufferedImage difference =
                new BufferedImage(
                        width,
                        height,
                        BufferedImage.TYPE_INT_RGB
                );

        /*
         * Difference is amplified only for
         * visualization.
         */
        int amplification = 25;

        for (int y = 0; y < height; y++) {

            for (int x = 0;
                 x < width;
                 x++) {

                int originalRGB =
                        original.getRGB(x, y);

                int poisonedRGB =
                        poisoned.getRGB(x, y);

                int r =
                        Math.abs(
                                red(originalRGB)
                                        - red(poisonedRGB)
                        );

                int g =
                        Math.abs(
                                green(originalRGB)
                                        - green(poisonedRGB)
                        );

                int b =
                        Math.abs(
                                blue(originalRGB)
                                        - blue(poisonedRGB)
                        );

                r = clamp(
                        r * amplification
                );

                g = clamp(
                        g * amplification
                );

                b = clamp(
                        b * amplification
                );

                difference.setRGB(
                        x,
                        y,
                        rgb(r, g, b)
                );
            }
        }

        return difference;
    }


    private int calculateMaximumDifference(
            BufferedImage original,
            BufferedImage poisoned
    ) {

        int maximum = 0;

        for (int y = 0;
             y < original.getHeight();
             y++) {

            for (int x = 0;
                 x < original.getWidth();
                 x++) {

                int a =
                        original.getRGB(x, y);

                int b =
                        poisoned.getRGB(x, y);

                maximum =
                        Math.max(
                                maximum,
                                Math.abs(
                                        red(a)
                                                - red(b)
                                )
                        );

                maximum =
                        Math.max(
                                maximum,
                                Math.abs(
                                        green(a)
                                                - green(b)
                                )
                        );

                maximum =
                        Math.max(
                                maximum,
                                Math.abs(
                                        blue(a)
                                                - blue(b)
                                )
                        );
            }
        }

        return maximum;
    }


    private long countChangedPixels(
            BufferedImage original,
            BufferedImage poisoned
    ) {

        long count = 0;

        for (int y = 0;
             y < original.getHeight();
             y++) {

            for (int x = 0;
                 x < original.getWidth();
                 x++) {

                if (original.getRGB(x, y)
                        != poisoned.getRGB(x, y)) {

                    count++;
                }
            }
        }

        return count;
    }


    private BufferedImage copyImage(
            BufferedImage source
    ) {

        BufferedImage copy =
                new BufferedImage(
                        source.getWidth(),
                        source.getHeight(),
                        BufferedImage.TYPE_INT_RGB
                );

        for (int y = 0;
             y < source.getHeight();
             y++) {

            for (int x = 0;
                 x < source.getWidth();
                 x++) {

                copy.setRGB(
                        x,
                        y,
                        source.getRGB(x, y)
                );
            }
        }

        return copy;
    }


    private void saveImage(
            BufferedImage image,
            String path
    ) throws IOException {

        File file = new File(path);

        File parent =
                file.getParentFile();

        if (parent != null) {
            parent.mkdirs();
        }

        ImageIO.write(
                image,
                "png",
                file
        );
    }


    private int red(int rgb) {

        return (rgb >> 16)
                & 0xFF;
    }


    private int green(int rgb) {

        return (rgb >> 8)
                & 0xFF;
    }


    private int blue(int rgb) {

        return rgb
                & 0xFF;
    }


    private int rgb(
            int r,
            int g,
            int b
    ) {

        return (r << 16)
                | (g << 8)
                | b;
    }


    private int clamp(int value) {

        return Math.max(
                0,
                Math.min(
                        255,
                        value
                )
        );
    }
}