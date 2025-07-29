import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.ReentrantReadWriteLock;
import java.util.function.Supplier;

public class DistributedTxManager {
    private static final long TIMEOUT_SECONDS = 5;
    
    private final Map<String, TransactionContext> transactions;
    private final Map<String, ServiceRegistration> services;
    private final ReentrantReadWriteLock txLock;
    private final ReentrantReadWriteLock serviceLock;
    
    public DistributedTxManager() {
        this.transactions = new ConcurrentHashMap<>();
        this.services = new ConcurrentHashMap<>();
        this.txLock = new ReentrantReadWriteLock();
        this.serviceLock = new ReentrantReadWriteLock();
    }

    public String startTransaction() {
        String txId = UUID.randomUUID().toString();
        TransactionContext context = new TransactionContext();
        txLock.writeLock().lock();
        try {
            transactions.put(txId, context);
        } finally {
            txLock.writeLock().unlock();
        }
        return txId;
    }

    public void registerService(String serviceId, 
                              Supplier<CompletableFuture<Boolean>> commitCallback,
                              Supplier<CompletableFuture<Boolean>> rollbackCallback) {
        ServiceRegistration registration = new ServiceRegistration(commitCallback, rollbackCallback);
        serviceLock.writeLock().lock();
        try {
            services.put(serviceId, registration);
        } finally {
            serviceLock.writeLock().unlock();
        }
    }

    public void enlistParticipant(String txId, String serviceId) {
        txLock.writeLock().lock();
        try {
            TransactionContext context = transactions.get(txId);
            if (context == null || context.getStatus() != TransactionStatus.ACTIVE) {
                throw new IllegalStateException("Transaction " + txId + " is not active");
            }
            context.addParticipant(serviceId);
        } finally {
            txLock.writeLock().unlock();
        }
    }

    public boolean commitTransaction(String txId) {
        TransactionContext context = transactions.get(txId);
        if (context == null) {
            return false;
        }

        // Ensure we only try to commit once
        if (!context.setCommitting()) {
            return false;
        }

        List<CompletableFuture<Boolean>> preparePhase = new ArrayList<>();
        Set<String> participants = context.getParticipants();

        // Phase 1: Prepare
        for (String serviceId : participants) {
            ServiceRegistration service = services.get(serviceId);
            if (service == null) continue;

            CompletableFuture<Boolean> future = service.commitCallback.get()
                .orTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .exceptionally(throwable -> false);
            preparePhase.add(future);
        }

        try {
            CompletableFuture<Void> allPrepare = CompletableFuture.allOf(
                preparePhase.toArray(new CompletableFuture[0]));
            
            allPrepare.get(TIMEOUT_SECONDS, TimeUnit.SECONDS);
            
            boolean allSuccess = preparePhase.stream()
                .allMatch(future -> {
                    try {
                        return future.get();
                    } catch (Exception e) {
                        return false;
                    }
                });

            if (allSuccess) {
                context.setStatus(TransactionStatus.COMMITTED);
                return true;
            } else {
                rollbackTransaction(txId, context, participants);
                return false;
            }
        } catch (Exception e) {
            rollbackTransaction(txId, context, participants);
            return false;
        }
    }

    private void rollbackTransaction(String txId, TransactionContext context, Set<String> participants) {
        List<CompletableFuture<Boolean>> rollbackPhase = new ArrayList<>();

        // Phase 2: Rollback
        for (String serviceId : participants) {
            ServiceRegistration service = services.get(serviceId);
            if (service == null) continue;

            CompletableFuture<Boolean> future = service.rollbackCallback.get()
                .exceptionally(throwable -> false);
            rollbackPhase.add(future);
        }

        try {
            CompletableFuture.allOf(rollbackPhase.toArray(new CompletableFuture[0]))
                .get(TIMEOUT_SECONDS, TimeUnit.SECONDS);
        } catch (Exception e) {
            // Log rollback failures but continue
            e.printStackTrace();
        }

        context.setStatus(TransactionStatus.ROLLED_BACK);
    }

    public TransactionStatus getTransactionStatus(String txId) {
        txLock.readLock().lock();
        try {
            TransactionContext context = transactions.get(txId);
            return context != null ? context.getStatus() : null;
        } finally {
            txLock.readLock().unlock();
        }
    }

    private static class TransactionContext {
        private final Set<String> participants;
        private volatile TransactionStatus status;
        private final ReentrantReadWriteLock participantsLock;
        private volatile boolean isCommitting;

        TransactionContext() {
            this.participants = ConcurrentHashMap.newKeySet();
            this.status = TransactionStatus.ACTIVE;
            this.participantsLock = new ReentrantReadWriteLock();
            this.isCommitting = false;
        }

        void addParticipant(String serviceId) {
            participantsLock.writeLock().lock();
            try {
                participants.add(serviceId);
            } finally {
                participantsLock.writeLock().unlock();
            }
        }

        Set<String> getParticipants() {
            participantsLock.readLock().lock();
            try {
                return new HashSet<>(participants);
            } finally {
                participantsLock.readLock().unlock();
            }
        }

        TransactionStatus getStatus() {
            return status;
        }

        void setStatus(TransactionStatus newStatus) {
            this.status = newStatus;
        }

        boolean setCommitting() {
            return !isCommitting && (isCommitting = true);
        }
    }

    private static class ServiceRegistration {
        final Supplier<CompletableFuture<Boolean>> commitCallback;
        final Supplier<CompletableFuture<Boolean>> rollbackCallback;

        ServiceRegistration(Supplier<CompletableFuture<Boolean>> commitCallback,
                          Supplier<CompletableFuture<Boolean>> rollbackCallback) {
            this.commitCallback = commitCallback;
            this.rollbackCallback = rollbackCallback;
        }
    }
}