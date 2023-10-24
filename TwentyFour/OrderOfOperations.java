/**
 * All possible order of operations for an arithmetic expression
 * with four operands and three operators
 */
public enum OrderOfOperations {
    _123("((%s %s %s) %s %s) %s %s"),
    _132("(%s %s %s) %s (%s %s %s)"),
    _231("%s %s ((%s %s %s) %s %s)"),
    _321("%s %s (%s %s (%s %s %s))");
    // Skip _312 and _213 which don't compute to different result

    private final String printPattern;

    OrderOfOperations(String printPattern) {
        this.printPattern = printPattern;
    }

    public final String printPattern() {
        return printPattern;
    }
}