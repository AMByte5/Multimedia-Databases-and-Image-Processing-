package org.example;

import org.example.operations.Attack;

public class Main {

    public static void main(String[] args) {

        String input =
                "C:\\Users\\LapTop 1\\OneDrive\\Desktop\\iiiiii\\image10.jpg";

        String poisoned =
                "C:\\Users\\LapTop 1\\OneDrive\\Desktop\\iiiiii\\poisoned_image.png";

        String difference =
                "C:\\Users\\LapTop 1\\OneDrive\\Desktop\\iiiiii\\difference_amplified.png";

        /*
         * Maximum perturbation:
         *
         * epsilon = 8/255
         */
        int epsilon = 8;

        /*
         * Number of candidate modifications.
         */
        int iterations = 2000;

        Attack attack =
                new Attack(
                        epsilon,
                        iterations
                );

        try {

            attack.poisonImage(
                    input,
                    poisoned,
                    difference
            );

        } catch (Exception e) {

            System.err.println(
                    "Attack failed:"
            );

            e.printStackTrace();
        }
    }
}