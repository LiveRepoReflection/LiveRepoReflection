import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class TransactionCoordinatorTest {

    // Interface representing a service endpoint.
    interface ServiceEndpoint {
        boolean prepare(String transactionId, String accountId, double amount, int expectedVersion);
        boolean commit(String transactionId);
        boolean rollback(String transactionId);
    }

    // Fake service endpoint for testing.
    class FakeServiceEndpoint implements ServiceEndpoint {
        private boolean prepareResult;
        private boolean commitResult;
        private int commitFailCount;
        private boolean timeoutOnPrepare;
        
        int prepareInvocations = 0;
        int commitInvocations = 0;
        int rollbackInvocations = 0;
        
        public FakeServiceEndpoint(boolean prepareResult, boolean commitResult) {
            this.prepareResult = prepareResult;
            this.commitResult = commitResult;
            this.commitFailCount = 0;
            this.timeoutOnPrepare = false;
        }
        
        public void setCommitFailCount(int count) {
            this.commitFailCount = count;
        }
        
        public void setTimeoutOnPrepare(boolean timeout) {
            this.timeoutOnPrepare = timeout;
        }
        
        @Override
        public boolean prepare(String transactionId, String accountId, double amount, int expectedVersion) {
            prepareInvocations++;
            if (timeoutOnPrepare) {
                // Simulate a timeout by sleeping longer than the allowed threshold.
                try {
                    Thread.sleep(2000);
                } catch (InterruptedException e) {
                    // Ignore interruption.
                }
                return false;
            }
            return prepareResult;
        }
        
        @Override
        public boolean commit(String transactionId) {
            commitInvocations++;
            if (commitFailCount > 0) {
                commitFailCount--;
                return false;
            }
            return commitResult;
        }
        
        @Override
        public boolean rollback(String transactionId) {
            rollbackInvocations++;
            // Always handle rollback successfully.
            return true;
        }
    }

    // Transaction request data structure for the transaction.
    class TransactionRequest {
        String transactionId;
        String serviceAAccountId;
        String serviceBAccountId;
        double amount;
        int serviceAExpectedVersion;
        int serviceBExpectedVersion;
        
        public TransactionRequest(String transactionId, String serviceAAccountId, String serviceBAccountId,
                                  double amount, int serviceAExpectedVersion, int serviceBExpectedVersion) {
            this.transactionId = transactionId;
            this.serviceAAccountId = serviceAAccountId;
            this.serviceBAccountId = serviceBAccountId;
            this.amount = amount;
            this.serviceAExpectedVersion = serviceAExpectedVersion;
            this.serviceBExpectedVersion = serviceBExpectedVersion;
        }
    }
    
    // DistributedTransactionCoordinator is assumed to be implemented by the candidate.
    // For testing purposes, we provide a minimal implementation that follows the two-phase commit protocol.
    class DistributedTransactionCoordinator {
        private ServiceEndpoint serviceA;
        private ServiceEndpoint serviceB;
        private int maxRetries = 3; // Maximum retries for commit/rollback operations.
        private int prepareTimeout = 1000; // Timeout in milliseconds for the prepare phase.
        
        public DistributedTransactionCoordinator(ServiceEndpoint serviceA, ServiceEndpoint serviceB) {
            this.serviceA = serviceA;
            this.serviceB = serviceB;
        }
        
        public String processTransaction(TransactionRequest request) {
            boolean aPrepared = false;
            boolean bPrepared = false;
            long startTime;
            
            // Prepare phase for Service A.
            startTime = System.currentTimeMillis();
            aPrepared = serviceA.prepare(request.transactionId, request.serviceAAccountId, request.amount, request.serviceAExpectedVersion);
            if (System.currentTimeMillis() - startTime > prepareTimeout) {
                aPrepared = false;
            }
            
            // Prepare phase for Service B.
            startTime = System.currentTimeMillis();
            bPrepared = serviceB.prepare(request.transactionId, request.serviceBAccountId, request.amount, request.serviceBExpectedVersion);
            if (System.currentTimeMillis() - startTime > prepareTimeout) {
                bPrepared = false;
            }
            
            // If both services prepared successfully, move to the commit phase.
            if (aPrepared && bPrepared) {
                boolean aCommitted = retryCommit(serviceA, request.transactionId);
                boolean bCommitted = retryCommit(serviceB, request.transactionId);
                if (aCommitted && bCommitted) {
                    return "SUCCESS";
                } else {
                    // On commit failure, rollback both services.
                    retryRollback(serviceA, request.transactionId);
                    retryRollback(serviceB, request.transactionId);
                    return "FAILURE";
                }
            } else {
                // If either prepare fails, trigger rollback.
                retryRollback(serviceA, request.transactionId);
                retryRollback(serviceB, request.transactionId);
                return "FAILURE";
            }
        }
        
        private boolean retryCommit(ServiceEndpoint service, String transactionId) {
            int attempts = 0;
            while (attempts < maxRetries) {
                if (service.commit(transactionId)) {
                    return true;
                }
                attempts++;
            }
            return false;
        }
        
        private boolean retryRollback(ServiceEndpoint service, String transactionId) {
            int attempts = 0;
            while (attempts < maxRetries) {
                if (service.rollback(transactionId)) {
                    return true;
                }
                attempts++;
            }
            return false;
        }
    }
    
    @Test
    public void testSuccessfulTransaction() {
        FakeServiceEndpoint serviceA = new FakeServiceEndpoint(true, true);
        FakeServiceEndpoint serviceB = new FakeServiceEndpoint(true, true);
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(serviceA, serviceB);
        
        TransactionRequest request = new TransactionRequest("tx123", "accA", "accB", 100.0, 1, 1);
        String result = coordinator.processTransaction(request);
        
        assertEquals("SUCCESS", result, "Transaction should succeed when both services prepare and commit successfully.");
        assertTrue(serviceA.prepareInvocations >= 1, "Service A prepare should be invoked at least once.");
        assertTrue(serviceB.prepareInvocations >= 1, "Service B prepare should be invoked at least once.");
        assertTrue(serviceA.commitInvocations >= 1, "Service A commit should be invoked at least once.");
        assertTrue(serviceB.commitInvocations >= 1, "Service B commit should be invoked at least once.");
    }
    
    @Test
    public void testFailureDueToServiceAPrepare() {
        FakeServiceEndpoint serviceA = new FakeServiceEndpoint(false, true);
        FakeServiceEndpoint serviceB = new FakeServiceEndpoint(true, true);
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(serviceA, serviceB);
        
        TransactionRequest request = new TransactionRequest("tx124", "accA", "accB", 200.0, 1, 1);
        String result = coordinator.processTransaction(request);
        
        assertEquals("FAILURE", result, "Transaction should fail when Service A prepare fails.");
        assertTrue(serviceA.rollbackInvocations >= 1, "Service A rollback should be invoked on prepare failure.");
        assertTrue(serviceB.rollbackInvocations >= 1, "Service B rollback should be invoked when one prepare fails.");
    }
    
    @Test
    public void testFailureDueToServiceBPrepare() {
        FakeServiceEndpoint serviceA = new FakeServiceEndpoint(true, true);
        FakeServiceEndpoint serviceB = new FakeServiceEndpoint(false, true);
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(serviceA, serviceB);
        
        TransactionRequest request = new TransactionRequest("tx125", "accA", "accB", 300.0, 1, 1);
        String result = coordinator.processTransaction(request);
        
        assertEquals("FAILURE", result, "Transaction should fail when Service B prepare fails.");
        assertTrue(serviceA.rollbackInvocations >= 1, "Service A rollback should be invoked when one prepare fails.");
        assertTrue(serviceB.rollbackInvocations >= 1, "Service B rollback should be invoked on prepare failure.");
    }
    
    @Test
    public void testCommitRetriesOnTransientFailure() {
        FakeServiceEndpoint serviceA = new FakeServiceEndpoint(true, true);
        FakeServiceEndpoint serviceB = new FakeServiceEndpoint(true, true);
        // Simulate transient commit failure for Service A: fail first 2 attempts, then succeed.
        serviceA.setCommitFailCount(2);
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(serviceA, serviceB);
        
        TransactionRequest request = new TransactionRequest("tx126", "accA", "accB", 400.0, 1, 1);
        String result = coordinator.processTransaction(request);
        
        assertEquals("SUCCESS", result, "Transaction should succeed when transient commit failures recover after retries.");
        assertTrue(serviceA.commitInvocations >= 3, "Service A commit should be retried until success.");
        assertTrue(serviceB.commitInvocations >= 1, "Service B commit should be invoked at least once.");
    }
    
    @Test
    public void testPrepareTimeoutInitiatesRollback() {
        FakeServiceEndpoint serviceA = new FakeServiceEndpoint(true, true);
        FakeServiceEndpoint serviceB = new FakeServiceEndpoint(true, true);
        // Simulate a timeout during Service B's prepare phase.
        serviceB.setTimeoutOnPrepare(true);
        
        DistributedTransactionCoordinator coordinator = new DistributedTransactionCoordinator(serviceA, serviceB);
        
        TransactionRequest request = new TransactionRequest("tx127", "accA", "accB", 500.0, 1, 1);
        String result = coordinator.processTransaction(request);
        
        assertEquals("FAILURE", result, "Transaction should fail when a prepare operation times out.");
        assertTrue(serviceA.rollbackInvocations >= 1, "Service A rollback should be triggered upon timeout.");
        assertTrue(serviceB.rollbackInvocations >= 1, "Service B rollback should be triggered upon timeout.");
    }
}