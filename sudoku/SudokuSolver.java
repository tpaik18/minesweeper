
/**
 * Sudoku solver
 */
import java.io.*;
import java.util.*;

public class SudokuSolver {
    public static final int BLANK = -1;
    static int[][] grid = new int[9][9];
    static ArrayList<Integer>[][] possiblesGrid = new ArrayList[9][9];

    public static ArrayList<Integer> POSSIBLES_SET = new ArrayList<Integer>(Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9));

    static void printGrid() {
        for (int i = 0; i < 9; i++) {
            System.out.println(Arrays.toString(grid[i]));
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

    static void computePossibles(int blank_i, int blank_j) {
        System.out.println("computePossibles " + blank_i + ", " + blank_j);
        ArrayList<Integer> possibles = (ArrayList<Integer>) POSSIBLES_SET.clone();
        for (int i = 0; i < 9; i++) {
            if (grid[i][blank_j] != BLANK) {
                possibles.remove(Integer.valueOf(grid[i][blank_j]));
                System.out.print(" c" + grid[i][blank_j]);
            }
        }
        for (int j = 0; j < 9; j++) {
            if (grid[blank_i][j] != BLANK) {
                possibles.remove(Integer.valueOf(grid[blank_i][j]));
                System.out.print(" r" + grid[blank_i][j]);
            }
        }
        int squareStartX = getSquareCorner(blank_i);
        int squareStartY = getSquareCorner(blank_j);
        for (int i = squareStartX; i < squareStartX + 3; i++) {
            for (int j = squareStartY; j < squareStartY + 3; j++) {
                if (grid[i][j] != BLANK) {
                    possibles.remove(Integer.valueOf(grid[i][j]));
                    System.out.print(" s" + grid[i][j]);
                }
            }
        }
        possiblesGrid[blank_i][blank_j] = possibles;
    }

    static void markAnswer(int blank_i, int blank_j, int answer) {
        grid[blank_i][blank_j] = answer;
        possiblesGrid[blank_i][blank_j] = null;
        // remove answer from all possibles of this blank's row, col, or square
        for (int i = 0; i < 9; i++) {
            if (i != blank_i && possiblesGrid[i][blank_j] != null) {
                possiblesGrid[i][blank_j].remove(Integer.valueOf(answer));
            }
        }
        for (int j = 0; j < 9; j++) {
            if (j != blank_j && possiblesGrid[blank_i][j] != null) {
                possiblesGrid[blank_i][j].remove(Integer.valueOf(answer));
            }
        }
        int squareStartX = getSquareCorner(blank_i);
        int squareStartY = getSquareCorner(blank_j);
        for (int i = squareStartX; i < squareStartX + 3; i++) {
            for (int j = squareStartY; j < squareStartY + 3; j++) {
                if ((i != blank_i || j != blank_j) && possiblesGrid[i][j] != null) {
                    possiblesGrid[i][j].remove(Integer.valueOf(answer));
                }
            }
        }
    }

    static int seeIfOnlyOnePossible(int blank_i, int blank_j) {
        System.out.print("seeIfOnlyOnePossible " + blank_i + ", " + blank_j);
        ArrayList<Integer> possibles = possiblesGrid[blank_i][blank_j];
        if (possibles.size() == 1) {
            int onlyChoice = possibles.get(0);
            markAnswer(blank_i, blank_j, onlyChoice);
            System.out.println("\n*** SOLVED (only possible) " + blank_i + ", " + blank_j + " = " + onlyChoice);
            return onlyChoice;
        } else {
            possiblesGrid[blank_i][blank_j] = possibles;
            System.out.println(" possibles " + possibles);
            return BLANK;
        }
    }

    static int seeIfAPossibleCantGoAnywhereElse(int blank_i, int blank_j) {
        for (int x : possiblesGrid[blank_i][blank_j]) {
            boolean thisPossibleExistsElsewhere = false;
            for (int i = 0; i < 9; i++) {
                if (i != blank_i) {
                    ArrayList<Integer> possiblesForOtherSquare = possiblesGrid[i][blank_j];
                    if (possiblesForOtherSquare != null && possiblesForOtherSquare.contains(x)) {
                        thisPossibleExistsElsewhere = true;
                        break;
                    }
                }
            }
            if (!thisPossibleExistsElsewhere) {
                markAnswer(blank_i, blank_j, x);
                System.out.println(
                        "\n*** SOLVED (only place for possible) " + blank_i + ", " + blank_j + " = " + x);
                return x;
            }
            thisPossibleExistsElsewhere = false;
            for (int j = 0; j < 9; j++) {
                if (j != blank_j) {
                    ArrayList<Integer> possiblesForOtherSquare = possiblesGrid[blank_i][j];
                    if (possiblesForOtherSquare != null && possiblesForOtherSquare.contains(x)) {
                        thisPossibleExistsElsewhere = true;
                        break;
                    }
                }
            }
            if (!thisPossibleExistsElsewhere) {
                markAnswer(blank_i, blank_j, x);
                System.out.println(
                        "\n*** SOLVED (only place for possible) " + blank_i + ", " + blank_j + " = " + x);
                return x;
            }
            int squareStartX = getSquareCorner(blank_i);
            int squareStartY = getSquareCorner(blank_j);
            thisPossibleExistsElsewhere = false;
            for (int i = squareStartX; i < squareStartX + 3; i++) {
                for (int j = squareStartY; j < squareStartY + 3; j++) {
                    if (i != blank_i || j != blank_j) {
                        ArrayList<Integer> possiblesForOtherSquare = possiblesGrid[i][j];
                        if (possiblesForOtherSquare != null && possiblesForOtherSquare.contains(x)) {
                            thisPossibleExistsElsewhere = true;
                            break;
                        }
                    }
                }
            }
            if (!thisPossibleExistsElsewhere) {
                markAnswer(blank_i, blank_j, x);
                System.out.println(
                        "\n*** SOLVED (only place for possible) " + blank_i + ", " + blank_j + " = " + x);
                return x;
            }
        }
        return BLANK;
    }

    static void testEachBlank() {
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
            System.out.println("I'm stuck");
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
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                if (grid[i][j] == BLANK) {
                    computePossibles(i, j);
                }
            }
        }
        while (!isSolved()) {
            testEachBlank();
        }
        printGrid();
    }
}