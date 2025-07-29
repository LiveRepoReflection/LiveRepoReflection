package distributed_tx;

import java.util.concurrent.atomic.AtomicBoolean;

public class MockParticipant implements Participant {
    private final String id;
    private final boolean alwaysSucceed;
    private final AtomicBoolean prepared = new AtomicBoolean(false);
    private final AtomicBoolean committed = new AtomicBoolean(false);
    private final AtomicBoolean rolledBack = new AtomicBoolean(false);
    private final AtomicBoolean failOnCommit = new AtomicBoolean(false);

    public MockParticipant(String id, boolean alwaysSucceed) {
        this.id = id;
        this.alwaysSucceed = alwaysSucceed;
    }

    public void simulateFailureOnCommit() {
        failOnCommit.set(true);
    }

    public boolean isCommitted() {
        return committed.get();
    }

    public boolean isRolledBack() {
        return rolledBack.get();
    }

    @Override
    public String getId() {
        return id;
    }

    @Override
    public boolean prepare(Transaction tx) {
        if (alwaysSucceed) {
            prepared.set(true);
            return true;
        } else {
            prepared.set(false);
            return false;
        }
    }

    @Override
    public boolean commit(Transaction tx) {
        if (failOnCommit.get()) {
            return false;
        }
        if (prepared.get()) {
            committed.set(true);
            return true;
        }
        return false;
    }

    @Override
    public boolean rollback(Transaction tx) {
        if (prepared.get() || committed.get()) {
            rolledBack.set(true);
            return true;
        }
        rolledBack.set(true);
        return true;
    }
}