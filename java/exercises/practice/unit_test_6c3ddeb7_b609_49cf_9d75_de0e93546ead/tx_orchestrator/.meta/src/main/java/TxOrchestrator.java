import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Comparator;

public class TxOrchestrator {
    private final ServiceExecutor serviceExecutor;
    private final List<ReentrantLock> serviceLocks;

    public TxOrchestrator() {
        this.serviceExecutor = new ServiceExecutor();
        this.serviceLocks = Collections.synchronizedList(new ArrayList<>());
    }

    public boolean executeTransaction(List<Operation> operations) {
        // Sort operations to prevent deadlocks
        operations.sort(Comparator.comparing(Operation::getServiceId));

        List<ReentrantLock> acquiredLocks = new ArrayList<>();
        List<Operation> executedOperations = new ArrayList<>();

        try {
            // Phase 1: Acquire locks and execute operations
            for (Operation op : operations) {
                ReentrantLock lock = getServiceLock(op.getServiceId());
                lock.lock();
                acquiredLocks.add(lock);

                boolean success = serviceExecutor.execute(op.getServiceId(), op.getOperationData());
                if (!success) {
                    // Compensation phase
                    compensate(executedOperations);
                    return false;
                }
                executedOperations.add(op);
            }
            return true;
        } finally {
            // Release all locks
            for (ReentrantLock lock : acquiredLocks) {
                if (lock.isHeldByCurrentThread()) {
                    lock.unlock();
                }
            }
        }
    }

    private void compensate(List<Operation> executedOperations) {
        // Execute compensations in reverse order
        for (int i = executedOperations.size() - 1; i >= 0; i--) {
            Operation op = executedOperations.get(i);
            serviceExecutor.compensate(op.getServiceId(), op.getCompensationData());
        }
    }

    private ReentrantLock getServiceLock(String serviceId) {
        synchronized (serviceLocks) {
            for (ReentrantLock lock : serviceLocks) {
                if (lock.toString().contains(serviceId)) {
                    return lock;
                }
            }
            ReentrantLock newLock = new ReentrantLock();
            serviceLocks.add(newLock);
            return newLock;
        }
    }
}