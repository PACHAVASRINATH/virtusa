import java.util.Scanner;

public class QuizSystem {

    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);
        boolean continuetheQuiz = true;

        System.out.println("Simple Java Quiz\n");

        while (continuetheQuiz) {

            int marks = 0;

            // Question 1
            System.out.println("1. Which language is platform independent?");
            System.out.println("A. C\nB. Java\nC. Python\nD. C++");
            String a1 = sc.nextLine();

            if (a1.equalsIgnoreCase("B")) {
                System.out.println("Correct\n");
                marks++;
            } else {
                System.out.println("Wrong (Answer: B)\n");
            }

            // Question 2
            System.out.println("2. Which keyword is used for inheritance?");
            System.out.println("A. implements\nB. extends\nC. inherits\nD. super");
            String a2 = sc.nextLine();

            if (a2.equalsIgnoreCase("B")) {
                System.out.println("Correct\n");
                marks++;
            } else {
                System.out.println("Wrong (Answer: B)\n");
            }

            // Question 3
            System.out.println("3. Entry point of Java program?");
            System.out.println("A. start()\nB. run()\nC. main()\nD. init()");
            String a3 = sc.nextLine();

            if (a3.equalsIgnoreCase("C")) {
                System.out.println("Correct\n");
                marks++;
            } else {
                System.out.println("Wrong (Answer: C)\n");
            }

            // Question 4
            System.out.println("4. Which is NOT primitive?");
            System.out.println("A. int\nB. float\nC. String\nD. char");
            String a4 = sc.nextLine();

            if (a4.equalsIgnoreCase("C")) {
                System.out.println("Correct\n");
                marks++;
            } else {
                System.out.println("Wrong (Answer: C)\n");
            }

            // Question 5
            System.out.println("5. JVM stands for?");
            System.out.println("A. Java Variable Machine\nB. Java Virtual Machine\nC. Java Verified Machine\nD. Java Value Machine");
            String a5 = sc.nextLine();

            if (a5.equalsIgnoreCase("B")) {
                System.out.println("Correct\n");
                marks++;
            } else {
                System.out.println("Wrong (Answer: B)\n");
            }

            // Final Result
            double percent = (marks / 5.0) * 100;

            System.out.println("Quiz Finished!");
            System.out.println("Score: " + marks + "/5");
            System.out.println("Percentage: " + percent + "%");

            // Replay option (custom style)
            System.out.print("\nTry again? type YES to continue: ");
            String input = sc.nextLine();

            if (!input.equalsIgnoreCase("YES")) {
                continuetheQuiz = false;
            }

            System.out.println();
        }

        System.out.println("Exiting Quiz. Thanks!");
        sc.close();
    }
}