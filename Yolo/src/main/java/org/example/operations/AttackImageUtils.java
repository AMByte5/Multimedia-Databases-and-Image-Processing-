
package org.example.operations;

import javax.imageio.ImageIO;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;

public final class AttackImageUtils {

    private AttackImageUtils() {
    }

    // Load an image
    public static BufferedImage loadImage(
            String path
    ) throws IOException {

        BufferedImage image =
                ImageIO.read(new File(path));

        if (image == null) {
            throw new IOException(
                    "Cannot load image: " + path
            );
        }

        return image;
    }

    // Copy the original image
    public static BufferedImage copyImage(
            BufferedImage source
    ) {

        BufferedImage copy = new BufferedImage(
                source.getWidth(),
                source.getHeight(),
                BufferedImage.TYPE_INT_RGB
        );

        for (int y = 0; y < source.getHeight(); y++) {
            for (int x = 0; x < source.getWidth(); x++) {

                copy.setRGB(
                        x,
                        y,
                        source.getRGB(x, y)
                );
            }
        }

        return copy;
    }

    // Keep pixel values between 0 and 255
    public static int clamp(int value) {
        return Math.max(0, Math.min(255, value));
    }

    // Combine RGB channels
    public static int rgb(int r, int g, int b) {
        return (clamp(r) << 16)
                | (clamp(g) << 8)
                | clamp(b);
    }

    // Create amplified difference image
    public static BufferedImage createDifference(
            BufferedImage original,
            BufferedImage modified
    ) {

        int width = original.getWidth();
        int height = original.getHeight();

        BufferedImage difference = new BufferedImage(
                width,
                height,
                BufferedImage.TYPE_INT_RGB
        );

        for (int y = 0; y < height; y++) {
            for (int x = 0; x < width; x++) {

                int a = original.getRGB(x, y);
                int b = modified.getRGB(x, y);

                int dr = Math.abs(
                        ((a >> 16) & 255)
                                - ((b >> 16) & 255)
                );

                int dg = Math.abs(
                        ((a >> 8) & 255)
                                - ((b >> 8) & 255)
                );

                int db = Math.abs(
                        (a & 255) - (b & 255)
                );

                difference.setRGB(
                        x,
                        y,
                        rgb(
                                clamp(dr * 25),
                                clamp(dg * 25),
                                clamp(db * 25)
                        )
                );
            }
        }

        return difference;
    }

    // Save both the modified image and difference image
    public static void saveResults(
            BufferedImage original,
            BufferedImage modified,
            String outputPath,
            String differencePath
    ) throws IOException {

        saveImage(modified, outputPath);

        BufferedImage difference =
                createDifference(original, modified);

        saveImage(difference, differencePath);

        System.out.println("Saved: " + outputPath);
        System.out.println("Saved: " + differencePath);
    }

    // Save PNG image
    public static void saveImage(
            BufferedImage image,
            String path
    ) throws IOException {

        File file = new File(path);
        File parent = file.getParentFile();

        if (parent != null
                && !parent.exists()
                && !parent.mkdirs()) {

            throw new IOException(
                    "Cannot create folder: " + parent
            );
        }

        if (!ImageIO.write(image, "png", file)) {
            throw new IOException(
                    "Cannot write PNG: " + path
            );
        }
    }
}
