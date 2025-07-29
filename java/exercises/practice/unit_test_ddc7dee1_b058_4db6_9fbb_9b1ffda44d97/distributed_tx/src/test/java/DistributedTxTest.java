import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;

public class DistributedTxTest {

    class MockService implements Service {
        private final String name;
        private final boolean prepareSuccess;
        private final boolean commitSuccess;
        private final boolean throwPrepareException;
        private final boolean throwCommitException;
        private int prepareCount = 0;
        private int commitCount = 0;

        MockService(String name, boolean prepareSuccess, boolean commitSuccess, 
                   boolean throwPrepareException, boolean throwCommitException) {
            this.name = name;
            this.prepareSuccess = prepareSuccess;
            this.commitSuccess = commitSuccess;
            this.throwPrepareException = throwPrepareException;
            this.throwCommitException = throwCommitException;
        }

        @Override
        public boolean prepare() throws Exception {
            prepareCount++;
            if (throwPrepareException) {
                throw new Exception("Prepare failed for " + name);
            }
            return prepareSuccess;
        }

        @Override
        public boolean commit() throws Exception {
            commitCount++;
            if (throwCommitException) {
                throw new Exception("Commit failed for " + name);
            }
            return commitSuccess;
        }
    }

    @Test
    public void testSuccessfulTransaction() throws Exception {
        List<Service> services = new ArrayList<>();
        services.add(new MockService("Service1", true, true, false, false));
        services.add(new MockService("Service2", true, true, false, false));
        services.add(new MockService("Service3", true, true, false, false));

        DistributedTx dtc = new DistributedTx();
        boolean result = dtc.transact(services);
        
        assertTrue(result);
        for (Service service : services) {
            MockService mock = (MockService) service;
            assertEquals(1, mock.prepareCount);
            assertEquals(1, mock.commitCount);
        }
    }

    @Test
    public void testPrepareFailure() throws Exception {
        List<Service> services = new ArrayList<>();
        services.add(new MockService("Service1", true, true, false, false));
        services.add(new MockService("Service2", false, true, false, false)); // Will fail prepare
        services.add(new MockService("Service3", true, true, false, false));

        DistributedTx dtc = new DistributedTx();
        boolean result = dtc.transact(services);
        
        assertFalse(result);
        for (Service service : services) {
            MockService mock = (MockService) service;
            assertEquals(1, mock.prepareCount);
            assertEquals(0, mock.commitCount); // No commit should be called
        }
    }

    @Test
    public void testPrepareException() throws Exception {
        List<Service> services = new ArrayList<>();
        services.add(new MockService("Service1", true, true, false, false));
        services.add(new MockService("Service2", true, true, true, false)); // Will throw on prepare
        services.add(new MockService("Service3", true, true, false, false));

        DistributedTx dtc = new DistributedTx();
        boolean result = dtc.transact(services);
        
        assertFalse(result);
        for (Service service : services) {
            MockService mock = (MockService) service;
            assertEquals(1, mock.prepareCount);
            assertEquals(0, mock.commitCount); // No commit should be called
        }
    }

    @Test
    public void testCommitFailure() throws Exception {
        List<Service> services = new ArrayList<>();
        services.add(new MockService("Service1", true, true, false, false));
        services.add(new MockService("Service2", true, false, false, false)); // Will fail commit
        services.add(new MockService("Service3", true, true, false, false));

        DistributedTx dtc = new DistributedTx();
        boolean result = dtc.transact(services);
        
        assertFalse(result);
        for (Service service : services) {
            MockService mock = (MockService) service;
            assertEquals(1, mock.prepareCount);
            assertEquals(1, mock.commitCount);
        }
    }

    @Test
    public void testCommitException() throws Exception {
        List<Service> services = new ArrayList<>();
        services.add(new MockService("Service1", true, true, false, false));
        services.add(new MockService("Service2", true, true, false, true)); // Will throw on commit
        services.add(new MockService("Service3", true, true, false, false));

        DistributedTx dtc = new DistributedTx();
        boolean result = dtc.transact(services);
        
        assertFalse(result);
        for (Service service : services) {
            MockService mock = (MockService) service;
            assertEquals(1, mock.prepareCount);
            assertEquals(1, mock.commitCount);
        }
    }

    @Test
    public void testEmptyServicesList() throws Exception {
        List<Service> services = new ArrayList<>();
        DistributedTx dtc = new DistributedTx();
        boolean result = dtc.transact(services);
        
        assertTrue(result); // Empty transaction should succeed
    }

    @Test
    public void testLargeNumberOfServices() throws Exception {
        List<Service> services = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            services.add(new MockService("Service" + i, true, true, false, false));
        }

        DistributedTx dtc = new DistributedTx();
        boolean result = dtc.transact(services);
        
        assertTrue(result);
        for (Service service : services) {
            MockService mock = (MockService) service;
            assertEquals(1, mock.prepareCount);
            assertEquals(1, mock.commitCount);
        }
    }

    @Test
    public void testConcurrentExecution() throws Exception {
        List<Service> services = new ArrayList<>();
        AtomicBoolean prepareStarted = new AtomicBoolean(false);
        AtomicBoolean prepareCompleted = new AtomicBoolean(false);

        // Add services that will coordinate to test concurrency
        for (int i = 0; i < 10; i++) {
            final int serviceNum = i;
            services.add(new MockService("Service" + i, true, true, false, false) {
                @Override
                public boolean prepare() throws Exception {
                    if (serviceNum == 0) prepareStarted.set(true);
                    while (serviceNum == 5 && !prepareStarted.get()) {
                        Thread.sleep(10);
                    }
                    if (serviceNum == 9) prepareCompleted.set(true);
                    return super.prepare();
                }
            });
        }

        DistributedTx dtc = new DistributedTx();
        boolean result = dtc.transact(services);
        
        assertTrue(result);
        assertTrue(prepareStarted.get());
        assertTrue(prepareCompleted.get());
        for (Service service : services) {
            MockService mock = (MockService) service;
            assertEquals(1, mock.prepareCount);
            assertEquals(1, mock.commitCount);
        }
    }
}