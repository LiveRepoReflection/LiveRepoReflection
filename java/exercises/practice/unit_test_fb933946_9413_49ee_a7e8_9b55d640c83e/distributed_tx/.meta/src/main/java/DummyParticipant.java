public class DummyParticipant implements Participant {
    private final String serviceName;
    private final long responseDelay;
    private final boolean failPrepare;
    private boolean prepared = false;
    private boolean committed = false;
    private boolean rolledBack = false;

    public DummyParticipant(String serviceName) {
        this(serviceName, 0L, false);
    }

    public DummyParticipant(String serviceName, long responseDelay, boolean failPrepare) {
        this.serviceName = serviceName;
        this.responseDelay = responseDelay;
        this.failPrepare = failPrepare;
    }
    
    @Override
    public String prepare() {
        try {
            if (responseDelay > 0) {
                Thread.sleep(responseDelay);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        if (failPrepare) {
            return "abort";
        } else {
            prepared = true;
            return "prepared";
        }
    }

    @Override
    public void commit() {
        committed = true;
    }

    @Override
    public void rollback() {
        rolledBack = true;
    }

    @Override
    public boolean isPrepared() {
        return prepared;
    }
    
    // Optional getters for additional introspection (e.g., in testing)
    public boolean isCommitted() {
        return committed;
    }

    public boolean isRolledBack() {
        return rolledBack;
    }
}