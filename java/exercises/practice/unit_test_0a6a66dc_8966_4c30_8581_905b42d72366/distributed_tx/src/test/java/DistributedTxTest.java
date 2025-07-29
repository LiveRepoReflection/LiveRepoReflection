import org.junit.Test;
import org.junit.Assert;
import java.util.*;
import java.util.concurrent.*;

public class DistributedTxTest {

    // Transaction status enumeration.
    public enum TransactionStatus {
        PREPARING, COMMITTED, ROLLED_BACK, FAILED
    }

    // Service interface that participating services should implement.
    public interface Service {
        boolean prepare(String transactionId);
        void commit(String transactionId);
        void rollback(String transactionId);
    }
    
    // A fake service to simulate real service behavior.
    public class FakeService implements Service {
        private boolean prepareSuccess;
        private long delayMillis;
        
        public boolean committed = false;
        public boolean rolledBack = false;
        public List<String> invocationLog = new ArrayList<>();
        
        public FakeService(boolean prepareSuccess) {
            this(prepareSuccess, 0);
        }
        
        public FakeService(boolean prepareSuccess, long delayMillis) {
            this.prepareSuccess = prepareSuccess;
            this.delayMillis = delayMillis;
        }
        
        @Override
        public boolean prepare(String transactionId) {
            invocationLog.add("prepare");
            if (delayMillis > 0) {
                try {
                    Thread.sleep(delayMillis);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }
            return prepareSuccess;
        }
        
        @Override
        public void commit(String transactionId) {
            invocationLog.add("commit");
            committed = true;
        }
        
        @Override
        public void rollback(String transactionId) {
            invocationLog.add("rollback");
            rolledBack = true;
        }
    }
    
    // DistributedTransactionCoordinator is assumed to be implemented as per the problem.
    // It should handle transaction coordination with methods to start a transaction and query its status.
    public class DistributedTransactionCoordinator {
        private ConcurrentMap<String, TransactionStatus> txStatusMap = new ConcurrentHashMap<>();
        
        public String startTransaction(List<Service> services) {
            String txId = UUID.randomUUID().toString();
            txStatusMap.put(txId, TransactionStatus.PREPARING);
            ExecutorService executor = Executors.newSingleThreadExecutor();
            executor.submit(() -> {
                boolean allPrepared = true;
                for (Service service : services) {
                    boolean prepared = service.prepare(txId);
                    if (!prepared) {
                        allPrepared = false;
                        break;
                    }
                }
                if (allPrepared) {
                    for (Service service : services) {
                        service.commit(txId);
                    }
                    txStatusMap.put(txId, TransactionStatus.COMMITTED);
                } else {
                    for (Service service : services) {
                        service.rollback(txId);
                    }
                    txStatusMap.put(txId, TransactionStatus.ROLLED_BACK);
                }
            });
            executor.shutdown();
            return txId;
        }
        
        public TransactionStatus getTransactionStatus(String txId) {
            return txStatusMap.get(txId);
        }
    }
    
    @Test
    public void testSuccessfulTransaction() throws Exception {
        List<Service> services = new ArrayList<>();
        FakeService s1 = new FakeService(true);
        FakeService s2 = new FakeService(true);
        services.add(s1);
        services.add(s2);
        
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        String txId = coordinator.startTransaction(services);
        
        waitForTransaction(coordinator, txId, 2000);
        
        TransactionStatus status = coordinator.getTransactionStatus(txId);
        Assert.assertEquals(TransactionStatus.COMMITTED, status);
        Assert.assertTrue(s1.committed);
        Assert.assertTrue(s2.committed);
    }
    
    @Test
    public void testFailedTransactionDueToPrepare() throws Exception {
        List<Service> services = new ArrayList<>();
        FakeService s1 = new FakeService(true);
        FakeService s2 = new FakeService(false);
        services.add(s1);
        services.add(s2);
        
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        String txId = coordinator.startTransaction(services);
        
        waitForTransaction(coordinator, txId, 2000);
        
        TransactionStatus status = coordinator.getTransactionStatus(txId);
        Assert.assertEquals(TransactionStatus.ROLLED_BACK, status);
        Assert.assertTrue(s1.rolledBack);
        Assert.assertTrue(s2.rolledBack);
    }
    
    @Test
    public void testTransactionInProgress() throws Exception {
        // Simulate delay to allow transaction to be in PREPARING state.
        List<Service> services = new ArrayList<>();
        FakeService s1 = new FakeService(true, 1000);
        FakeService s2 = new FakeService(true, 1000);
        services.add(s1);
        services.add(s2);
        
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        String txId = coordinator.startTransaction(services);
        
        // Immediately check the status; it should be PREPARING.
        TransactionStatus initialStatus = coordinator.getTransactionStatus(txId);
        Assert.assertEquals(TransactionStatus.PREPARING, initialStatus);
        
        waitForTransaction(coordinator, txId, 3000);
        TransactionStatus finalStatus = coordinator.getTransactionStatus(txId);
        Assert.assertEquals(TransactionStatus.COMMITTED, finalStatus);
    }
    
    @Test
    public void testConcurrentTransactions() throws Exception {
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator();
        int transactionCount = 10;
        List<String> txIds = new ArrayList<>();
        List<FakeService> serviceInstances = new ArrayList<>();
        
        for (int i = 0; i < transactionCount; i++) {
            List<Service> services = new ArrayList<>();
            // Alternate between transactions that succeed and fail.
            boolean prepareSuccess = (i % 2 == 0);
            FakeService service = new FakeService(prepareSuccess);
            services.add(service);
            serviceInstances.add(service);
            String txId = coordinator.startTransaction(services);
            txIds.add(txId);
        }
        
        for (String txId : txIds) {
            waitForTransaction(coordinator, txId, 2000);
        }
        
        for (int i = 0; i < transactionCount; i++) {
            TransactionStatus status = coordinator.getTransactionStatus(txIds.get(i));
            if (i % 2 == 0) {
                Assert.assertEquals(TransactionStatus.COMMITTED, status);
                Assert.assertTrue(serviceInstances.get(i).committed);
            } else {
                Assert.assertEquals(TransactionStatus.ROLLED_BACK, status);
                Assert.assertTrue(serviceInstances.get(i).rolledBack);
            }
        }
    }
    
    private void waitForTransaction(DistributedTransactionCoordinator coordinator, String txId, long timeoutMillis) throws Exception {
        long startTime = System.currentTimeMillis();
        while (System.currentTimeMillis() - startTime < timeoutMillis) {
            TransactionStatus status = coordinator.getTransactionStatus(txId);
            if (status == TransactionStatus.COMMITTED ||
                status == TransactionStatus.ROLLED_BACK ||
                status == TransactionStatus.FAILED) {
                return;
            }
            Thread.sleep(50);
        }
    }
}