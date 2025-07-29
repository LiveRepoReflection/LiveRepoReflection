public class TestMicroservice implements MicroserviceOperation {
    private final String name;
    private final boolean prepareSuccess;
    private boolean committed;
    private boolean rolledBack;
    private int commitCount;
    private final long artificialDelay; // in milliseconds

    public TestMicroservice(String name, boolean prepareSuccess) {
        this(name, prepareSuccess, 0);
    }

    public TestMicroservice(String name, boolean prepareSuccess, long artificialDelay) {
        this.name = name;
        this.prepareSuccess = prepareSuccess;
        this.artificialDelay = artificialDelay;
        this.committed = false;
        this.rolledBack = false;
        this.commitCount = 0;
    }

    @Override
    public boolean prepare(long timeout) throws InterruptedException {
        if (artificialDelay > 0) {
            if (artificialDelay > timeout) {
                Thread.sleep(timeout);
                return false;
            } else {
                Thread.sleep(artificialDelay);
            }
        }
        return prepareSuccess;
    }

    @Override
    public void commit() {
        // Ensure idempotency: allow commit only once.
        if (!committed) {
            committed = true;
            commitCount++;
        }
    }

    @Override
    public void rollback() {
        rolledBack = true;
    }

    public boolean isCommitted() {
        return committed;
    }

    public boolean isRolledBack() {
        return rolledBack;
    }

    public int getCommitCount() {
        return commitCount;
    }

    public String getName() {
        return name;
    }
}