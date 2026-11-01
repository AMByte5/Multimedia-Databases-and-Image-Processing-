
package org.example;

import org.example.operations.AdversarialPatchAttack;
import org.example.operations.SquareAttack;
import org.example.operations.SimBAAttack;
import org.example.operations.PGDAttack;

import java.io.File;

public class Main {

    public static void main(String[] args) {

        // =====================================
        // ATTACK TRIGGERS
        // =====================================

        boolean useAdversarialPatch = true;
        boolean useSquareAttack = false;
        boolean useSimBAAttack = false;
        boolean usePGDAttack = false;

        // =====================================
        // INPUT IMAGE
        // =====================================

        String input =
                "C:\\Users\\LapTop 1\\OneDrive\\Desktop\\iiiiii\\image17.jpg";

        // =====================================
        // ATTACK PARAMETERS
        // =====================================

        int epsilon = 8;
        int iterations = 2000;

        // =====================================
        // GET ORIGINAL IMAGE NAME
        // =====================================

        File inputFile = new File(input);

        String fileName = inputFile.getName();

        int dotIndex = fileName.lastIndexOf('.');

        String imageName = dotIndex > 0
                ? fileName.substring(0, dotIndex)
                : fileName;

        String folder = inputFile.getParent();

        // =====================================
        // RUN ATTACKS
        // =====================================

        if (useAdversarialPatch) {

            try {

                String attackName = "AdversarialPatch";

                String poisoned = new File(
                        folder,
                        imageName + "_" + attackName + ".png"
                ).getPath();

                String difference = new File(
                        folder,
                        imageName + "_" + attackName
                                + "_difference.png"
                ).getPath();

                AdversarialPatchAttack attack =
                        new AdversarialPatchAttack(
                                epsilon, iterations
                        );

                attack.poisonImage(
                        input, poisoned, difference
                );

            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        if (useSquareAttack) {

            try {

                String attackName = "SquareAttack";

                String poisoned = new File(
                        folder,
                        imageName + "_" + attackName + ".png"
                ).getPath();

                String difference = new File(
                        folder,
                        imageName + "_" + attackName
                                + "_difference.png"
                ).getPath();

                SquareAttack attack =
                        new SquareAttack(
                                epsilon, iterations
                        );

                attack.poisonImage(
                        input, poisoned, difference
                );

            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        if (useSimBAAttack) {

            try {

                String attackName = "SimBAAttack";

                String poisoned = new File(
                        folder,
                        imageName + "_" + attackName + ".png"
                ).getPath();

                String difference = new File(
                        folder,
                        imageName + "_" + attackName
                                + "_difference.png"
                ).getPath();

                SimBAAttack attack =
                        new SimBAAttack(
                                epsilon, iterations
                        );

                attack.poisonImage(
                        input, poisoned, difference
                );

            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        if (usePGDAttack) {

            try {

                String attackName = "PGDAttack";

                String poisoned = new File(
                        folder,
                        imageName + "_" + attackName + ".png"
                ).getPath();

                String difference = new File(
                        folder,
                        imageName + "_" + attackName
                                + "_difference.png"
                ).getPath();

                PGDAttack attack =
                        new PGDAttack(
                                epsilon, iterations
                        );

                attack.poisonImage(
                        input, poisoned, difference
                );

            } catch (Exception e) {
                e.printStackTrace();
            }
        }

        System.out.println("Finished running enabled attacks.");
    }
}
