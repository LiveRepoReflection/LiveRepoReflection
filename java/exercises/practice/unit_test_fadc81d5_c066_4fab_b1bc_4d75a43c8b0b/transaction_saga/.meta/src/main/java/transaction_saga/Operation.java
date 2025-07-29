package transaction_saga;

public interface Operation {
    /**
     * Executes the operation.
     * @return true if the operation is successful, false otherwise.
     */
    boolean execute();

    /**
     * Compensates or rolls back the operation.
     * @return true if the compensation is successful, false otherwise.
     */
    boolean compensate();

    /**
     * Returns the name of the operation.
     * @return the operation name.
     */
    String getName();
}