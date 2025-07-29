import java.util.concurrent.atomic.AtomicLong;
import java.util.Map;
import java.util.HashMap;
import java.util.List;
import java.util.ArrayList;
import java.util.Set;
import java.util.HashSet;

public class TransactionCoordinator {

    private final long timeout;
    private final AtomicLong txnIdCounter = new AtomicLong(1);
    private final Map<Long, Transaction> transactions = new HashMap<>();
    private final Map<Long, ResourceLock> resourceLocks = new HashMap<>();

    public TransactionCoordinator(long timeoutMs) {
        this.timeout = timeoutMs;
    }

    public synchronized long begin() {
        long tid = txnIdCounter.getAndIncrement();
        Transaction txn = new Transaction(tid);
        transactions.put(tid, txn);
        return tid;
    }

    public synchronized boolean commit(long tid) {
        Transaction txn = transactions.get(tid);
        if (txn == null || txn.state != TransactionState.ACTIVE) {
            return false;
        }
        // Release all acquired locks
        for (Long resourceId : new ArrayList<>(txn.heldLocks.keySet())) {
            ResourceLock rlock = resourceLocks.get(resourceId);
            if (rlock != null && rlock.ownerTid == tid) {
                // Fully release lock held by the transaction
                rlock.ownerTid = 0;
                rlock.lockCount = 0;
                notifyAll();
            }
        }
        txn.heldLocks.clear();
        txn.state = TransactionState.COMMITTED;
        return true;
    }

    public synchronized boolean rollback(long tid) {
        Transaction txn = transactions.get(tid);
        if (txn == null || txn.state != TransactionState.ACTIVE) {
            return false;
        }
        // Release all acquired locks
        for (Long resourceId : new ArrayList<>(txn.heldLocks.keySet())) {
            ResourceLock rlock = resourceLocks.get(resourceId);
            if (rlock != null && rlock.ownerTid == tid) {
                rlock.ownerTid = 0;
                rlock.lockCount = 0;
                notifyAll();
            }
        }
        txn.heldLocks.clear();
        txn.state = TransactionState.ABORTED;
        return true;
    }

    public boolean acquireLock(long tid, long resourceId) throws InterruptedException {
        long startWait = System.currentTimeMillis();
        synchronized (this) {
            Transaction txn = transactions.get(tid);
            if (txn == null || txn.state != TransactionState.ACTIVE) {
                return false;
            }
            ResourceLock rlock = resourceLocks.get(resourceId);
            if (rlock == null) {
                rlock = new ResourceLock(resourceId);
                resourceLocks.put(resourceId, rlock);
            }
            // If resource is free or owned by the same transaction (reentrant locking)
            if (rlock.ownerTid == 0 || rlock.ownerTid == tid) {
                rlock.acquire(tid);
                txn.addLock(resourceId);
                return true;
            } else {
                if (!rlock.waiting.contains(tid)) {
                    rlock.waiting.add(tid);
                }
            }
        }
        long remaining = timeout - (System.currentTimeMillis() - startWait);
        while (remaining > 0) {
            synchronized (this) {
                Transaction txn = transactions.get(tid);
                if (txn == null || txn.state != TransactionState.ACTIVE) {
                    return false;
                }
                ResourceLock rlock = resourceLocks.get(resourceId);
                if (rlock.ownerTid == 0 || rlock.ownerTid == tid) {
                    rlock.waiting.remove(tid);
                    rlock.acquire(tid);
                    txn.addLock(resourceId);
                    return true;
                }
                // Trigger deadlock detection if waiting for more than half the timeout period
                if (System.currentTimeMillis() - startWait > timeout / 2) {
                    detectAndResolveDeadlock();
                }
            }
            Thread.sleep(50);
            remaining = timeout - (System.currentTimeMillis() - startWait);
        }
        synchronized (this) {
            ResourceLock rlock = resourceLocks.get(resourceId);
            if (rlock != null) {
                rlock.waiting.remove(tid);
            }
            rollback(tid);
            notifyAll();
        }
        return false;
    }

    public synchronized boolean releaseLock(long tid, long resourceId) {
        Transaction txn = transactions.get(tid);
        if (txn == null || !txn.heldLocks.containsKey(resourceId)) {
            return false;
        }
        ResourceLock rlock = resourceLocks.get(resourceId);
        if (rlock != null && rlock.ownerTid == tid) {
            rlock.release();
            if (rlock.ownerTid == 0 && !rlock.waiting.isEmpty()) {
                notifyAll();
            }
            txn.removeLock(resourceId);
            return true;
        }
        return false;
    }

    private void detectAndResolveDeadlock() {
        // Build wait-for graph (edge: waiting transaction -> owner transaction)
        Map<Long, Set<Long>> graph = new HashMap<>();
        for (ResourceLock rlock : resourceLocks.values()) {
            if (rlock.ownerTid != 0) {
                for (Long waitingTid : rlock.waiting) {
                    graph.computeIfAbsent(waitingTid, k -> new HashSet<>()).add(rlock.ownerTid);
                }
            }
        }
        // Detect cycle using DFS
        Set<Long> cycle = new HashSet<>();
        for (Long txnId : graph.keySet()) {
            Set<Long> visited = new HashSet<>();
            if (dfsDetect(txnId, txnId, graph, visited)) {
                cycle.addAll(visited);
                break;
            }
        }
        if (!cycle.isEmpty()) {
            // Select victim transaction: one with fewest locks held and latest start time
            long victimTid = -1;
            int minLocks = Integer.MAX_VALUE;
            long latestStart = -1;
            for (Long t : cycle) {
                Transaction txn = transactions.get(t);
                if (txn != null && txn.state == TransactionState.ACTIVE) {
                    int locksHeld = txn.heldLocks.size();
                    if (locksHeld < minLocks || (locksHeld == minLocks && txn.startTime > latestStart)) {
                        victimTid = t;
                        minLocks = locksHeld;
                        latestStart = txn.startTime;
                    }
                }
            }
            if (victimTid != -1) {
                rollback(victimTid);
                notifyAll();
            }
        }
    }

    private boolean dfsDetect(Long current, Long target, Map<Long, Set<Long>> graph, Set<Long> visited) {
        if (current.equals(target) && !visited.isEmpty()) {
            return true;
        }
        if (visited.contains(current)) {
            return false;
        }
        visited.add(current);
        Set<Long> neighbours = graph.getOrDefault(current, new HashSet<>());
        for (Long neighbour : neighbours) {
            if (dfsDetect(neighbour, target, graph, visited)) {
                return true;
            }
        }
        return false;
    }

    public synchronized void shutdown() {
        transactions.clear();
        resourceLocks.clear();
    }

    private class Transaction {
        long tid;
        TransactionState state;
        long startTime;
        Map<Long, Integer> heldLocks = new HashMap<>();

        Transaction(long tid) {
            this.tid = tid;
            this.state = TransactionState.ACTIVE;
            this.startTime = System.currentTimeMillis();
        }

        void addLock(long resourceId) {
            heldLocks.put(resourceId, heldLocks.getOrDefault(resourceId, 0) + 1);
        }

        void removeLock(long resourceId) {
            if (heldLocks.containsKey(resourceId)) {
                int count = heldLocks.get(resourceId);
                if (count <= 1) {
                    heldLocks.remove(resourceId);
                } else {
                    heldLocks.put(resourceId, count - 1);
                }
            }
        }
    }

    private class ResourceLock {
        long resourceId;
        long ownerTid;
        int lockCount;
        List<Long> waiting = new ArrayList<>();

        ResourceLock(long resourceId) {
            this.resourceId = resourceId;
            this.ownerTid = 0;
            this.lockCount = 0;
        }

        void acquire(long tid) {
            if (ownerTid == tid) {
                lockCount++;
            } else {
                ownerTid = tid;
                lockCount = 1;
            }
        }

        void release() {
            if (lockCount > 1) {
                lockCount--;
            } else {
                ownerTid = 0;
                lockCount = 0;
            }
        }
    }

    private enum TransactionState {
        ACTIVE, COMMITTED, ABORTED
    }
}