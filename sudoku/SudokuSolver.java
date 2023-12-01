
/**
 * Sudoku solver
 */
import java.io.*;
import java.util.*;

public class SudokuSolver {
    public static final int BLANK = -1;
    public static ArrayList<Integer> POSSIBLES_SET = new ArrayList<Integer>(Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9));
    static int[][] grid = new int[9][9];

    // first dimension is the possible numbers 1-9, second and third dimensions are
    // the grid coords. Java initializes to false
    static boolean[][][] possiblesGrid = new boolean[9][9][9];

    static void printGrid() {
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                System.out.print(grid[i][j] == BLANK ? " " : grid[i][j]);
                if (j < 8) {
                    System.out.print(",");
                }
            }
            System.out.println();
        }
    }

    static boolean isSolved() {
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                if (grid[i][j] == BLANK) {
                    return false;
                }
            }
        }
        return true;
    }

    static int numberFromCsv(String token) {
        if (token.equals(" ")) {
            return BLANK;
        } else {
            return Integer.parseInt(token);
        }
    }

    static void readGridFromFile(String csvFilename) {
        try {
            Scanner sc = new Scanner(new File(csvFilename));
            sc.useDelimiter(",");
            int i = 0, j = 0;
            while (sc.hasNext()) {
                String nextToken = sc.next();
                if (nextToken.length() == 1) {
                    grid[i][j++] = numberFromCsv(nextToken);
                } else { // contains line break
                    grid[i][j] = numberFromCsv(nextToken.substring(0, 1));
                    i++;
                    j = 0;
                    if (i < 9) {
                        grid[i][j++] = numberFromCsv(nextToken.substring(nextToken.length() - 1));
                    }
                }
            }
            sc.close();
        } catch (IOException e) {
            System.err.println(e);
        }
    }

    // find the index of the upper left corner of the 3x3 square that contains this
    static int getSquareCorner(int index) {
        return Math.floorDiv(index, 3) * 3;
    }

    static boolean rowContains(int i, int possible) {
        for (int j = 0; j < 9; j++) {
            if (grid[i][j] == possible) {
                return true;
            }
        }
        return false;
    }

    static boolean colContains(int j, int possible) {
        for (int i = 0; i < 9; i++) {
            if (grid[i][j] == possible) {
                return true;
            }
        }
        return false;
    }

    static boolean squareContains(int i, int j, int possible) {
        int cornerX = getSquareCorner(i);
        int cornerY = getSquareCorner(j);
        for (int x = cornerX; x < cornerX + 3; x++) {
            for (int y = cornerY; y < cornerY + 3; y++) {
                if (grid[x][y] == possible) {
                    return true;
                }
            }
        }
        return false;
    }

    // "Possibles" are called "Hints" in sudoku sites -- the small numbers you write
    // in as possible candidates for this square
    static void computePossibles() {
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                if (grid[i][j] != BLANK) {
                    continue;
                }
                for (int possible : POSSIBLES_SET) {
                    possiblesGrid[possible - 1][i][j] = !(rowContains(i, possible) || colContains(j, possible)
                            || squareContains(i, j, possible));
                }
            }
        }
    }

    static void markAnswer(int blank_i, int blank_j, int answer) {
        grid[blank_i][blank_j] = answer;
        // remove answer from all possibles of this blank's row, col, or square
        for (int i = 0; i < 9; i++) {
            possiblesGrid[answer - 1][i][blank_j] = false;
        }
        for (int j = 0; j < 9; j++) {
            possiblesGrid[answer - 1][blank_i][j] = false;
        }
        int cornerX = getSquareCorner(blank_i);
        int cornerY = getSquareCorner(blank_j);
        for (int i = cornerX; i < cornerX + 3; i++) {
            for (int j = cornerY; j < cornerY + 3; j++) {
                possiblesGrid[answer - 1][i][j] = false;
            }
        }
    }

    static int seeIfOnlyOnePossible(int blank_i, int blank_j) {
        System.out.print("seeIfOnlyOnePossible " + blank_i + ", " + blank_j);
        ArrayList<Integer> choices = new ArrayList<Integer>();
        for (int x : POSSIBLES_SET) {
            if (possiblesGrid[x - 1][blank_i][blank_j]) {
                choices.add(x);
            }
        }
        if (choices.size() == 1) {
            int onlyChoice = choices.get(0);
            markAnswer(blank_i, blank_j, onlyChoice);
            System.out.println("\n*** SOLVED (only possible) " + blank_i + ", " + blank_j + " = " + onlyChoice);
            return onlyChoice;
        } else {
            System.out.println(" possibles " + choices);
            return BLANK;
        }
    }

    // TODO FIX UP THIS METHOD
    static int seeIfAPossibleCantGoAnywhereElse(int blank_i, int blank_j) {
        for (int x : POSSIBLES_SET) {
            if (possiblesGrid[x - 1][blank_i][blank_j]) {
                // check row to see if all others false
                ArrayList<Boolean> thisRowPossibles = Arrays.asList(possiblesGrid[x - 1][blank_i]);
                // check col to see if all others false
                // check square to see if all others false
            }
        }

        if (!thisPossibleExistsInCol || !thisPossibleExistsInRow || !thisPossibleExistsInSquare) {
            markAnswer(blank_i, blank_j, x);
            System.out.println(
                    "\n*** SOLVED (only place for possible) " + blank_i + ", " + blank_j + " = " + x);
            return x;
        }
        return BLANK;
    }

    // Main logic: Scan entire grid looking for solvable squares
    // If went through the whole grid and couldn't solve anything, we're stuck
    static void solveMoreBlanks() {
        boolean dirty = false;
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                if (grid[i][j] == BLANK
                        && (seeIfOnlyOnePossible(i, j) != BLANK || seeIfAPossibleCantGoAnywhereElse(i, j) != BLANK)) {
                    dirty = true;
                }
            }
        }
        if (!dirty) {
            System.out.println("SHUCKS I'M STUCK");
            printGrid();
            System.exit(1);
        }
    }

    public static void main(String[] args) {
        if (args.length < 1) {
            System.err.println("First argument must be the grid CSV filename");
            System.exit(1);
        }
        readGridFromFile(args[0]);
        computePossibles();
        while (!isSolved()) {
            solveMoreBlanks();
        }
        printGrid();
    }
}