
/**
 * Sudoku solver
 */
import java.io.*;
import java.util.*;

public class SudokuSolver {
    public static final int BLANK = -1;
    static int[][] grid = new int[9][9];
    static ArrayList<Integer>[][] possibles;
    static {
    }

    public static ArrayList<Integer> SUDOKU_SET = new ArrayList<Integer>(Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9));

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

    static void initialize(String csvFilename) {
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

    static int solveByRow(int blank_i, int blank_j) {
        ArrayList<Integer> sudokuSet = (ArrayList<Integer>) SUDOKU_SET.clone();
        for (int j = 0; j < 9; j++) {
            if (j != blank_j) {
                sudokuSet.remove(Integer.valueOf(grid[blank_i][j] - 1));
            }
        }
        if (sudokuSet.size() == 1) {
            int onlyChoice = sudokuSet.get(0);
            grid[blank_i][blank_j] = onlyChoice;
            return onlyChoice;
        } else {
            return BLANK;
        }
    }

    static int solveByCol(int blank_i, int blank_j) {
        ArrayList<Integer> sudokuSet = (ArrayList<Integer>) SUDOKU_SET.clone();
        for (int i = 0; i < 9; i++) {
            if (i != blank_i) {
                sudokuSet.remove(Integer.valueOf(grid[i][blank_j]));
            }
        }
        if (sudokuSet.size() == 1) {
            int onlyChoice = sudokuSet.get(0);
            grid[blank_i][blank_j] = onlyChoice;
            return onlyChoice;
        } else {
            return BLANK;
        }
    }

    static int solveBySquare(int blank_i, int blank_j) {
        ArrayList<Integer> sudokuSet = (ArrayList<Integer>) SUDOKU_SET.clone();
        int squareStartX = Math.floorDiv(blank_i, 3) * 3;
        int squareStartY = Math.floorDiv(blank_j, 3) * 3;
        for (int i = squareStartX; i < squareStartX + 3; i++) {
            for (int j = squareStartY; j < squareStartY + 3; j++) {
                if (i != blank_i || j != blank_j) {
                    sudokuSet.remove(Integer.valueOf(grid[i][j]));
                }
            }
        }
        if (sudokuSet.size() == 1) {
            int onlyChoice = sudokuSet.get(0);
            grid[blank_i][blank_j] = onlyChoice;
            return onlyChoice;
        } else {
            return BLANK;
        }
    }

    static int solveBlankIfPossible(int blank_i, int blank_j) {
        System.out.println("solveBlankIfPossible " + blank_i + ", " + blank_j);
        ArrayList<Integer> sudokuSet = (ArrayList<Integer>) SUDOKU_SET.clone();
        for (int i = 0; i < 9; i++) {
            if (grid[i][blank_j] != BLANK) {
                sudokuSet.remove(Integer.valueOf(grid[i][blank_j]));
                System.out.println("removed " + grid[i][blank_j]);
            }
        }
        for (int j = 0; j < 9; j++) {
            if (grid[blank_i][j] != BLANK) {
                sudokuSet.remove(Integer.valueOf(grid[blank_i][j]));
                System.out.println("removed " + grid[blank_i][j]);
            }
        }
        int squareStartX = Math.floorDiv(blank_i, 3) * 3;
        int squareStartY = Math.floorDiv(blank_j, 3) * 3;
        for (int i = squareStartX; i < squareStartX + 3; i++) {
            for (int j = squareStartY; j < squareStartY + 3; j++) {
                if (grid[i][j] != BLANK) {
                    sudokuSet.remove(Integer.valueOf(grid[i][j]));
                    System.out.println("removed " + grid[i][j]);
                }
            }
        }
        if (sudokuSet.size() == 1) {
            int onlyChoice = sudokuSet.get(0);
            grid[blank_i][blank_j] = onlyChoice;
            return onlyChoice;
        } else {
            System.out.println("sudokuSet " + sudokuSet);
            return BLANK;
        }
        // if (solveByRow(blank_i, blank_j) == BLANK) {
        // if (solveByCol(blank_i, blank_j) == BLANK) {
        // if (solveBySquare(blank_i, blank_j) == BLANK) {
        // System.out.println("didn't solve " + blank_i + ", " + blank_j);
        // return BLANK;
        // }
        // }
        // }
        // return grid[blank_i][blank_j];
    }

    static void testEachBlank() {
        boolean dirty = false;
        for (int i = 0; i < 9; i++) {
            for (int j = 0; j < 9; j++) {
                if (grid[i][j] == BLANK) {
                    int answer = solveBlankIfPossible(i, j);
                    if (answer != BLANK) {
                        dirty = true;
                        System.out.println("Solved " + i + ", " + j + " = " + answer);
                    }
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
        initialize(args[0]);
        while (!isSolved()) {
            testEachBlank();
        }
    }
}