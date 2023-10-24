
/**
 * Helper for the Chinese game "24" where you draw a random four cards from a 52-card deck
 * and see if there's an arithmetic expression using the four cards that equals 24
 */
import java.util.*;

public class TwentyFour {

    static ArrayList<char[]> operatorCombos = new ArrayList<char[]>();
    // 4^3 possible combinations of operators in the expression
    static {
        char[] operators = { '+', '-', '*', '/' };
        for (char firstOperator : operators) {
            for (char secondOperator : operators) {
                for (char thirdOperator : operators) {
                    char[] operatorCombo = new char[] { firstOperator, secondOperator, thirdOperator };
                    operatorCombos.add(operatorCombo);
                }
            }
        }
    }

    private static ArrayList<int[]> getOperandCombos(int[] cards) {
        ArrayList<int[]> operandCombos = new ArrayList<int[]>();
        // 4! possible orderings of the cards
        findPermutation(cards, 4, operandCombos);
        return operandCombos;
    }

    // finds permutation using Heap Algorithm
    static void findPermutation(int array[], int size, ArrayList<int[]> list) {
        // if size becomes 1, add obtained permutation to list
        if (size == 1) {
            list.add(Arrays.copyOf(array, array.length));
        }
        for (int i = 0; i < size; i++) {
            findPermutation(array, size - 1, list);
            // if length of the array is odd, swap 0th element with last element
            if (size % 2 == 1) {
                int temp = array[0];
                array[0] = array[size - 1];
                array[size - 1] = temp;
            } else {
                // if length of the array is even, swap ith element with last element
                int temp = array[i];
                array[i] = array[size - 1];
                array[size - 1] = temp;
            }
        }
    }

    private static Solution getSolution(int[] hand) {
        ArrayList<int[]> operandCombos = getOperandCombos(hand);
        for (int[] operands : operandCombos) {
            for (char[] operators : operatorCombos) {
                for (OrderOfOperations order : OrderOfOperations.values()) {
                    Solution s = new Solution(operands, operators, order);
                    double result = s.compute();
                    if (result >= 23.9999 && result <= 24.0001) {
                        // equals 24 due to floating point precision loss
                        return s;
                    }
                }
            }
        }
        return null;
    }

    /**
     * Read four numbers in from stdin (accept j, q, k for 11, 12, 13)
     * and display the solution if it exists, otherwise display "NO SOLUTION"
     */
    public static void interactiveTwentyFour() {
        Scanner scanner = new Scanner(System.in);
        System.out.print("Enter four numbers: ");
        scanner.useDelimiter("[\s\\W]+"); // comma or whitespace or both
        int[] cards = new int[4];
        for (int i = 0; i < 4; i++) {
            int card;
            String input = scanner.next().toUpperCase();
            switch (input) {
                case "A":
                    card = 1;
                    break;
                case "J":
                    card = 11;
                    break;
                case "Q":
                    card = 12;
                    break;
                case "K":
                    card = 13;
                    break;
                default:
                    card = Integer.parseInt(input);
                    break;
            }
            cards[i] = card;
        }
        scanner.close();
        Solution solution = getSolution(cards);
        if (solution != null) {
            System.out.println("Solution: " + solution.stringify());
        } else {
            System.out.println("NO SOLUTION.");
        }
    }

    /**
     * Compute the probability that a random hand is solvable i.e.
     * the percent of possible hands that are solvable
     */
    public static void computePercentHandsSolvable() {
        HashSet<Integer> allPossibleHands = new HashSet<Integer>();
        // simulate drawing four random cards from a deck of 52
        for (int a = 0; a < 52; a++) {
            for (int b = 0; b < 52; b++) {
                if (b == a) {
                    continue;
                }
                for (int c = 0; c < 52; c++) {
                    if (c == a || c == b) {
                        continue;
                    }
                    for (int d = 0; d < 52; d++) {
                        if (d == a || d == b || d == c) {
                            continue;
                        }
                        int[] hand = new int[] { a, b, c, d };
                        // sort to make sure the hand is unique
                        Arrays.sort(hand);
                        // hash into a single int to speed up HashSet dupe detection
                        int handNotation = hand[0] * 1000000 + hand[1] * 10000 + hand[2] * 100 + hand[3];
                        allPossibleHands.add(handNotation);
                    }
                }
            }
        }
        int numSolvable = 0;
        int numHands = allPossibleHands.size();
        System.out.printf("Testing %d possibilities...\n", numHands);
        long startTime = System.currentTimeMillis();
        for (Integer handNotation : allPossibleHands) {
            int[] hand = new int[4];
            hand[0] = Math.floorDiv(handNotation, 1000000) % 13 + 1;
            hand[1] = Math.floorDiv(handNotation % 1000000, 10000) % 13 + 1;
            hand[2] = Math.floorDiv(handNotation % 10000, 100) % 13 + 1;
            hand[3] = handNotation % 100 % 13 + 1;
            Solution solution = getSolution(hand);
            if (solution != null) {
                numSolvable++;
            }
        }
        long endTime = System.currentTimeMillis();
        System.out.printf("%d solvable hands out of %d = %.3f%%\n", numSolvable, numHands,
                numSolvable * 100.0 / numHands);
        System.out.printf("Ran in %.2f seconds", (endTime - startTime) / 1000.0);
    }

    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("--test")) {
            computePercentHandsSolvable();
        } else {
            interactiveTwentyFour();

        }
    }

}
