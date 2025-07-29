import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.locks.*;

public class TransactionManager {
    private final Map<Integer, Microservice> microservices = new ConcurrentHashMap<>();
    private final Map<Integer, TransactionState> transactionStates = new ConcurrentHashMap<>();
    private final Lock transactionLock = new ReentrantLock();
    private final long prepareTimeout = 2000; // 2 seconds timeout
    
    public void registerMicroservice(int id, Microservice microservice) {
        microservices.put(id, microservice);
    }
    
    public boolean executeTransaction(List<Integer> involvedMicroservices, List<List<Operation>> operationsPerService) {
        if (involvedMicroservices.size() != operationsPerService.size()) {
            throw new IllegalArgumentException("Services and operations lists must match in size");
        }
        
        int transactionId = generateTransactionId();
        transactionStates.put(transactionId, new TransactionState(TransactionPhase.PREPARE));
        
        try {
            // Phase 1: Prepare
            boolean allPrepared = preparePhase(transactionId, involvedMicroservices, operationsPerService);
            
            // Phase 2: Commit or Rollback
            if (allPrepared) {
                return commitPhase(transactionId, involvedMicroservices);
            } else {
                rollbackPhase(transactionId, involvedMicroservices);
                return false;
            }
        } finally {
            transactionStates.remove(transactionId);
        }
    }
    
    private boolean preparePhase(int transactionId, List<Integer> services, List<List<Operation>> operations) {
        ExecutorService executor = Executors.newFixedThreadPool(services.size());
        List<Future<Boolean>> futures = new ArrayList<>();
        
        for (int i = 0; i < services.size(); i++) {
            final int serviceId = services.get(i);
            final List<Operation> serviceOps = operations.get(i);
            futures.add(executor.submit(() -> {
                Microservice microservice = microservices.get(serviceId);
                if (microservice == null) return false;
                
                try {
                    String response = microservice.prepare(transactionId, serviceOps);
                    return "prepared".equals(response);
                } catch (Exception e) {
                    return false;
                }
            }));
        }
        
        executor.shutdown();
        
        try {
            boolean allSuccess = true;
            for (Future<Boolean> future : futures) {
                try {
                    if (!future.get(prepareTimeout, TimeUnit.MILLISECONDS)) {
                        allSuccess = false;
                    }
                } catch (TimeoutException | ExecutionException e) {
                    allSuccess = false;
                }
            }
            return allSuccess;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return false;
        }
    }
    
    private boolean commitPhase(int transactionId, List<Integer> services) {
        transactionStates.put(transactionId, new TransactionState(TransactionPhase.COMMIT));
        boolean allCommitted = true;
        
        for (int serviceId : services) {
            Microservice microservice = microservices.get(serviceId);
            if (microservice == null) continue;
            
            try {
                String response = microservice.commit(transactionId);
                if (!"ack".equals(response)) {
                    allCommitted = false;
                }
            } catch (Exception e) {
                allCommitted = false;
            }
        }
        
        return allCommitted;
    }
    
    private void rollbackPhase(int transactionId, List<Integer> services) {
        transactionStates.put(transactionId, new TransactionState(TransactionPhase.ROLLBACK));
        
        for (int serviceId : services) {
            Microservice microservice = microservices.get(serviceId);
            if (microservice == null) continue;
            
            try {
                microservice.rollback(transactionId);
            } catch (Exception e) {
                // Log failure but continue with other services
            }
        }
    }
    
    private int generateTransactionId() {
        return ThreadLocalRandom.current().nextInt(Integer.MAX_VALUE);
    }
    
    private enum TransactionPhase {
        PREPARE, COMMIT, ROLLBACK
    }
    
    private static class TransactionState {
        private final TransactionPhase phase;
        
        public TransactionState(TransactionPhase phase) {
            this.phase = phase;
        }
        
        public TransactionPhase getPhase() {
            return phase;
        }
    }
}