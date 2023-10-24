/**
 * Represents one specific ordering of cards, specific set of operators, and a
 * fixed order of operation. It may or may not resolve to 24.
 * Perhaps should be called "SolutionAttempt".
 * Eliminating this class improves performance by ~8%.
 */
public class Solution {
    int[] operands;
    char[] operators;
    OrderOfOperations orderOfOperations;

    Solution(int[] operands, char[] operators, OrderOfOperations orderOfOperations) {
        this.operands = operands;
        this.operators = operators;
        this.orderOfOperations = orderOfOperations;
    }

    double simpleCompute(double a, double b, char operator) {
        switch (operator) {
            case '+':
                return a + b;
            case '-':
                return a - b;
            case '*':
                return a * b;
            case '/':
                return a / b;
            default: // shouldn't happen
                throw new IllegalArgumentException("Unrecognized operator: " + operator);
        }
    }

    double compute() {
        switch (orderOfOperations) {
            case _123:
                return simpleCompute(
                        simpleCompute(simpleCompute(operands[0], operands[1], operators[0]), operands[2], operators[1]),
                        operands[3], operators[2]);
            case _132:
                return simpleCompute(
                        simpleCompute(operands[0], operands[1], operators[0]),
                        simpleCompute(operands[2], operands[3], operators[2]),
                        operators[1]);
            case _231:
                return simpleCompute(operands[0],
                        simpleCompute(simpleCompute(operands[1], operands[2], operators[1]),
                                operands[3], operators[2]),
                        operators[0]);
            case _321:
                return simpleCompute(operands[0],
                        simpleCompute(operands[1], simpleCompute(operands[2], operands[3],
                                operators[2]), operators[1]),
                        operators[0]);
            default: // shouldn't happen
                throw new IllegalArgumentException("Unrecognized orderOfOperations: " + orderOfOperations);
        }
    }

    String stringify() {
        return String.format(orderOfOperations.printPattern(), operands[0], operators[0], operands[1], operators[1],
                operands[2], operators[2], operands[3]);
    }
}
