import java.util.Scanner;

public class PasswordValidator {

    public static void main(String[] args) {

        Scanner sc = new Scanner(System.in);

        System.out.println("PASSWORD REQUIREMENTS:");
        System.out.println("Minimum 8 characters");
        System.out.println("At least 1 uppercase letter");
        System.out.println("At least 1 digit");
        System.out.println("At least 1 special character\n");

        while (true) {

            System.out.print("Enter password: ");
            String pswd = sc.nextLine();

            boolean hasUpper = false;
            boolean hasDigit = false;
            boolean hasSpecialchar = false;

            if (pswd.length() < 8) {
                System.out.println("Password must be at least 8 characters\n");
                continue;
            }

            for (int i = 0; i < pswd.length(); i++) {
                char ch = pswd.charAt(i);

                if (Character.isUpperCase(ch)) {
                    hasUpper = true;
                } else if (Character.isDigit(ch)) {
                    hasDigit = true;
                } else if (!Character.isLetterOrDigit(ch)) {
                    hasSpecialchar = true;
                }
            }

            if (!hasUpper) {
                System.out.println("Missing uppercase letter");
            }
            if (!hasDigit) {
                System.out.println("Missing digit");
            }
            if (!hasSpecialchar) {
                System.out.println("Missing special character");
            }

            if (hasUpper && hasDigit && hasSpecialchar) {
                System.out.println("Password accepted!");
                break;
            } else {
                System.out.println("Try again...\n");
            }
        }

        sc.close();
    }
}