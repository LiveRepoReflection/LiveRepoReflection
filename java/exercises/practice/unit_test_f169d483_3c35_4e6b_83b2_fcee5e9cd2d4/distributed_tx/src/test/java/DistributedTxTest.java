import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.Executors;

import static org.junit.jupiter.api.Assertions.*;

public class DistributedTxTest {

    // List to track all fake service servers created during tests, so we can stop them later.
    private final List<HttpServer> servers = new ArrayList<>();

    // Helper class to simulate service behavior
    private static class FakeServiceHandler implements HttpHandler {
        private final boolean prepareSuccess;
        private final boolean commitSuccess;
        private final boolean rollbackSuccess;

        public FakeServiceHandler(boolean prepareSuccess, boolean commitSuccess, boolean rollbackSuccess) {
            this.prepareSuccess = prepareSuccess;
            this.commitSuccess = commitSuccess;
            this.rollbackSuccess = rollbackSuccess;
        }

        @Override
        public void handle(HttpExchange exchange) throws IOException {
            String path = exchange.getRequestURI().getPath();
            int responseCode = 500;
            if (path.startsWith("/prepare/")) {
                responseCode = prepareSuccess ? 200 : 500;
            } else if (path.startsWith("/commit/")) {
                responseCode = commitSuccess ? 200 : 500;
            } else if (path.startsWith("/rollback/")) {
                responseCode = rollbackSuccess ? 200 : 500;
            }
            String response = "Response " + responseCode;
            exchange.sendResponseHeaders(responseCode, response.length());
            try (OutputStream os = exchange.getResponseBody()) {
                os.write(response.getBytes());
            }
            exchange.close();
        }
    }

    // Helper method to create and start a fake HTTP service
    private String startFakeService(boolean prepareSuccess, boolean commitSuccess, boolean rollbackSuccess) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(0), 0);
        server.createContext("/prepare", new FakeServiceHandler(prepareSuccess, commitSuccess, rollbackSuccess));
        server.createContext("/commit", new FakeServiceHandler(prepareSuccess, commitSuccess, rollbackSuccess));
        server.createContext("/rollback", new FakeServiceHandler(prepareSuccess, commitSuccess, rollbackSuccess));
        server.setExecutor(Executors.newCachedThreadPool());
        server.start();
        servers.add(server);
        int port = server.getAddress().getPort();
        return "http://localhost:" + port;
    }

    @BeforeEach
    public void setUp() {
        servers.clear();
    }

    @AfterEach
    public void tearDown() {
        for (HttpServer server : servers) {
            server.stop(0);
        }
        servers.clear();
    }

    // Test case 1: All services respond successfully on both prepare and commit phases.
    @Test
    public void testSuccessfulTransaction() throws Exception {
        // Create 3 fake services that always succeed.
        List<String> serviceUrls = new ArrayList<>();
        serviceUrls.add(startFakeService(true, true, true));
        serviceUrls.add(startFakeService(true, true, true));
        serviceUrls.add(startFakeService(true, true, true));

        // Assume DistributedTransactionManager exists with a method executeTransaction(List<String>) 
        // that returns an object of type TransactionResult with method isSuccessful()
        DistributedTransactionManager dtm = new DistributedTransactionManager();
        TransactionResult result = dtm.executeTransaction(serviceUrls);

        // Expect transaction to complete successfully.
        assertTrue(result.isSuccessful(), "Transaction should complete successfully when all services succeed.");
    }

    // Test case 2: One service fails in the prepare phase, resulting in a rollback.
    @Test
    public void testPrepareFailureTransaction() throws Exception {
        List<String> serviceUrls = new ArrayList<>();
        // Two services succeed, one fails in prepare.
        serviceUrls.add(startFakeService(true, true, true));
        serviceUrls.add(startFakeService(false, true, true)); // Will fail at prepare.
        serviceUrls.add(startFakeService(true, true, true));

        DistributedTransactionManager dtm = new DistributedTransactionManager();
        TransactionResult result = dtm.executeTransaction(serviceUrls);

        // Transaction should fail due to prepare failure.
        assertFalse(result.isSuccessful(), "Transaction should fail if any service fails during prepare.");
    }

    // Test case 3: One service fails in the commit phase after successful prepare.
    @Test
    public void testCommitFailureTransaction() throws Exception {
        List<String> serviceUrls = new ArrayList<>();
        // Two services commit successfully, one fails during commit.
        serviceUrls.add(startFakeService(true, true, true));
        serviceUrls.add(startFakeService(true, false, true)); // Will fail at commit.
        serviceUrls.add(startFakeService(true, true, true));

        DistributedTransactionManager dtm = new DistributedTransactionManager();
        TransactionResult result = dtm.executeTransaction(serviceUrls);

        // Transaction should be marked as failure due to commit failure.
        assertFalse(result.isSuccessful(), "Transaction should fail if any service fails during commit.");
    }

    // Test case 4: Simulate network delay or timeout by delaying response.
    @Test
    public void testTimeoutHandling() throws Exception {
        // Create a fake service that delays its response on prepare.
        HttpServer delayedServer = HttpServer.create(new InetSocketAddress(0), 0);
        delayedServer.createContext("/prepare", new HttpHandler() {
            @Override
            public void handle(HttpExchange exchange) throws IOException {
                try {
                    // Delay longer than the expected timeout period.
                    Thread.sleep(3000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                String response = "Delayed OK";
                exchange.sendResponseHeaders(200, response.length());
                try (OutputStream os = exchange.getResponseBody()) {
                    os.write(response.getBytes());
                }
                exchange.close();
            }
        });
        // Normal contexts for commit and rollback.
        delayedServer.createContext("/commit", new FakeServiceHandler(true, true, true));
        delayedServer.createContext("/rollback", new FakeServiceHandler(true, true, true));
        delayedServer.setExecutor(Executors.newCachedThreadPool());
        delayedServer.start();
        servers.add(delayedServer);

        List<String> serviceUrls = new ArrayList<>();
        serviceUrls.add("http://localhost:" + delayedServer.getAddress().getPort());
        serviceUrls.add(startFakeService(true, true, true));

        DistributedTransactionManager dtm = new DistributedTransactionManager();
        TransactionResult result = dtm.executeTransaction(serviceUrls);

        // Expect the transaction to eventually fail due to timeout on one service.
        assertFalse(result.isSuccessful(), "Transaction should fail if a service times out.");
    }

    // Test case 5: Concurrency - multiple transactions running concurrently.
    @Test
    public void testConcurrentTransactions() throws Exception {
        // Create a set of fake services that always succeed.
        final int numberOfServices = 3;
        final int concurrentTransactions = 5;
        final List<String> baseServiceUrls = new ArrayList<>();
        for (int i = 0; i < numberOfServices; i++) {
            baseServiceUrls.add(startFakeService(true, true, true));
        }

        final List<Thread> threads = new ArrayList<>();
        final List<TransactionResult> results = new ArrayList<>();
        // Synchronization for results addition.
        final Object lock = new Object();

        for (int i = 0; i < concurrentTransactions; i++) {
            Thread t = new Thread(() -> {
                DistributedTransactionManager dtm = new DistributedTransactionManager();
                TransactionResult result = dtm.executeTransaction(baseServiceUrls);
                synchronized (lock) {
                    results.add(result);
                }
            });
            threads.add(t);
            t.start();
        }
        for (Thread t : threads) {
            t.join();
        }
        // Check that all concurrent transactions succeed.
        for (TransactionResult result : results) {
            assertTrue(result.isSuccessful(), "Each concurrent transaction should succeed.");
        }
    }
}