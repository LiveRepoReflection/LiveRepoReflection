import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Test;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.atomic.AtomicBoolean;
import static org.junit.jupiter.api.Assertions.*;

public class DistributedTxTest {
    private DistributedTx dtc = new DistributedTx();

    @AfterEach
    public void tearDown() {
        dtc.shutdown();
    }

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
        services.add(new MockService("Service2", false, true, false, false));
        services.add(new MockService("Service3", true, true, false, false));

        boolean result = dtc.transact(services);
        assertFalse(result);
        for (Service service : services) {
            MockService mock = (MockService) service;
            assertEquals(1, mock.prepareCount);
            assertEquals(0, mock.commitCount);
        }
    }

    @Test
    public void testCommitFailureWithRetries() throws Exception {
        List<Service> services = new ArrayList<>();
        services.add(new MockService("Service1", true, true, false, false));
        services.add(new MockService("Service2", true, false, false, false));
        services.add(new MockService("Service3", true, true, false, false));

        boolean result = dtc.transact(services);
        assertFalse(result);
        for (Service service : services) {
            MockService mock = (MockService) service;
            assertEquals(1, mock.prepareCount);
            if (mock.name.equals("Service2")) {
                assertEquals(3, mock.commitCount);
            } else {
                assertEquals(1, mock.commitCount);
            }
        }
    }

    @Test
    public void testLargeNumberOfServices() throws Exception {
        List<Service> services = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            services.add(new MockService("Service" + i, true, true, false, false));
        }

        boolean result = dtc.transact(services);
        assertTrue(result);
    }
}