import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

class TransactionManagerTest {

    private TransactionManager transactionManager;
    private Map<String, Service> services;

    @BeforeEach
    void setUp() {
        services = new HashMap<>();
        services.put("service1", new MockService("service1"));
        services.put("service2", new MockService("service2"));
        services.put("service3", new MockService("service3"));
        
        transactionManager = new TransactionManager(services);
    }

    @Test
    @Timeout(value = 5000, unit = TimeUnit.MILLISECONDS)
    void testSuccessfulTransaction() throws ExecutionException, InterruptedException {
        // Create a transaction with operations for multiple services
        Transaction transaction = new Transaction("tx1");
        transaction.addOperation("service1", "operation1");
        transaction.addOperation("service2", "operation2");

        CompletableFuture<Boolean> result = transactionManager.executeTransaction(transaction);
        
        assertThat(result.get()).isTrue();
        assertThat(((MockService)services.get("service1")).isCommitted()).isTrue();
        assertThat(((MockService)services.get("service2")).isCommitted()).isTrue();
    }

    @Test
    @Timeout(value = 5000, unit = TimeUnit.MILLISECONDS)
    void testTransactionRollbackWhenOneServiceFails() throws InterruptedException {
        // Make service2 always fail during prepare phase
        ((MockService)services.get("service2")).setFailPrepare(true);

        Transaction transaction = new Transaction("tx2");
        transaction.addOperation("service1", "operation1");
        transaction.addOperation("service2", "operation2");

        CompletableFuture<Boolean> result = transactionManager.executeTransaction(transaction);

        assertThatThrownBy(() -> result.get())
            .isInstanceOf(ExecutionException.class)
            .hasMessageContaining("Transaction rolled back");

        assertThat(((MockService)services.get("service1")).isRolledBack()).isTrue();
        assertThat(((MockService)services.get("service2")).isRolledBack()).isTrue();
    }

    @Test
    @Timeout(value = 5000, unit = TimeUnit.MILLISECONDS)
    void testConcurrentTransactions() throws ExecutionException, InterruptedException {
        int numTransactions = 10;
        List<CompletableFuture<Boolean>> futures = new java.util.ArrayList<>();

        for (int i = 0; i < numTransactions; i++) {
            Transaction tx = new Transaction("tx" + i);
            tx.addOperation("service1", "operation" + i);
            tx.addOperation("service2", "operation" + i);
            futures.add(transactionManager.executeTransaction(tx));
        }

        CompletableFuture<Void> allFutures = CompletableFuture.allOf(
            futures.toArray(new CompletableFuture[0])
        );

        allFutures.get();

        for (CompletableFuture<Boolean> future : futures) {
            assertThat(future.get()).isTrue();
        }
    }

    @Test
    @Timeout(value = 5000, unit = TimeUnit.MILLISECONDS)
    void testTransactionTimeout() {
        // Make service1 sleep longer than timeout
        ((MockService)services.get("service1")).setResponseDelay(2000);

        Transaction transaction = new Transaction("tx3");
        transaction.addOperation("service1", "operation1");

        CompletableFuture<Boolean> result = transactionManager.executeTransaction(transaction);

        assertThatThrownBy(() -> result.get())
            .isInstanceOf(ExecutionException.class)
            .hasMessageContaining("Transaction timed out");
    }

    @Test
    @Timeout(value = 5000, unit = TimeUnit.MILLISECONDS)
    void testRetryMechanism() throws ExecutionException, InterruptedException {
        // Make service1 fail twice then succeed
        ((MockService)services.get("service1")).setFailuresBeforeSuccess(2);

        Transaction transaction = new Transaction("tx4");
        transaction.addOperation("service1", "operation1");

        CompletableFuture<Boolean> result = transactionManager.executeTransaction(transaction);
        
        assertThat(result.get()).isTrue();
        assertThat(((MockService)services.get("service1")).getAttemptCount()).isGreaterThan(2);
    }

    @Test
    @Timeout(value = 5000, unit = TimeUnit.MILLISECONDS)
    void testLargeTransaction() throws ExecutionException, InterruptedException {
        Transaction transaction = new Transaction("tx5");
        // Add 1000 operations
        for (int i = 0; i < 1000; i++) {
            transaction.addOperation("service1", "operation" + i);
            transaction.addOperation("service2", "operation" + i);
            transaction.addOperation("service3", "operation" + i);
        }

        CompletableFuture<Boolean> result = transactionManager.executeTransaction(transaction);
        
        assertThat(result.get()).isTrue();
    }

    // Mock implementation of Service interface for testing
    private static class MockService implements Service {
        private final String id;
        private boolean failPrepare = false;
        private long responseDelay = 0;
        private int failuresBeforeSuccess = 0;
        private int attemptCount = 0;
        private boolean committed = false;
        private boolean rolledBack = false;

        public MockService(String id) {
            this.id = id;
        }

        public void setFailPrepare(boolean failPrepare) {
            this.failPrepare = failPrepare;
        }

        public void setResponseDelay(long responseDelay) {
            this.responseDelay = responseDelay;
        }

        public void setFailuresBeforeSuccess(int failuresBeforeSuccess) {
            this.failuresBeforeSuccess = failuresBeforeSuccess;
        }

        public int getAttemptCount() {
            return attemptCount;
        }

        public boolean isCommitted() {
            return committed;
        }

        public boolean isRolledBack() {
            return rolledBack;
        }

        @Override
        public boolean prepare(String txId, String operation) {
            attemptCount++;
            
            if (responseDelay > 0) {
                try {
                    Thread.sleep(responseDelay);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return false;
                }
            }

            if (failuresBeforeSuccess > 0) {
                failuresBeforeSuccess--;
                return false;
            }

            return !failPrepare;
        }

        @Override
        public void commit(String txId) {
            committed = true;
        }

        @Override
        public void rollback(String txId) {
            rolledBack = true;
        }
    }
}