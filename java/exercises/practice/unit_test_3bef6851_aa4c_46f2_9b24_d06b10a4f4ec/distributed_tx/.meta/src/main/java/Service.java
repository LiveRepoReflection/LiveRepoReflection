package distributed_tx;

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.locks.ReentrantLock;

public class Service {
    private int id;
    private int resource;
    private int pendingDelta;
    private final ReentrantLock lock;
    private boolean forceFailure;

    public Service(int id, int initialResource) {
        this.id = id;
        this.resource = initialResource;
        this.pendingDelta = 0;
        this.lock = new ReentrantLock();
        this.forceFailure = false;
    }

    public int getId() {
        return id;
    }

    public int getResource() {
        return resource;
    }

    public void setForceFailure(boolean forceFailure) {
        this.forceFailure = forceFailure;
    }

    public ReentrantLock getLock() {
        return lock;
    }

    public void setResource(int value) {
        this.resource = value;
    }

    // Prepare phase: simulate tentative execution.
    // Returns true if the service votes commit, or false if it votes abort.
    public boolean prepare(List<TransactionOperation> ops) {
        if (forceFailure) {
            System.out.println("Service " + id + " forced failure during prepare.");
            return false;
        }
        if (ThreadLocalRandom.current().nextDouble() < 0.1) {
            System.out.println("Service " + id + " random internal failure during prepare.");
            return false;
        }
        int delta = 0;
        for (TransactionOperation op : ops) {
            if (op.getOperationType() == OperationType.INCREMENT) {
                delta += op.getAmount();
            } else if (op.getOperationType() == OperationType.DECREMENT) {
                delta -= op.getAmount();
            }
        }
        if (resource + delta < 0) {
            System.out.println("Service " + id + " has insufficient resource. Current: " + resource + ", Requested delta: " + delta);
            return false;
        }
        pendingDelta = delta;
        System.out.println("Service " + id + " prepared with pending delta: " + pendingDelta);
        return true;
    }

    // Commit phase: permanently apply the pending changes.
    public void commit() {
        resource += pendingDelta;
        System.out.println("Service " + id + " committed. New resource: " + resource);
        pendingDelta = 0;
    }

    // Rollback phase: discard tentative changes.
    public void rollback() {
        System.out.println("Service " + id + " rolled back. Resource remains: " + resource);
        pendingDelta = 0;
    }
}