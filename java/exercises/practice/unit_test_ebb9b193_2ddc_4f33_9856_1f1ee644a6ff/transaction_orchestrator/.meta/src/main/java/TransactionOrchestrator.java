import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public class TransactionOrchestrator {
    private final List<Service> services;
    private final int MAX_ROLLBACK_RETRIES = 3;

    public TransactionOrchestrator(List<Service> services) {
        // Make a defensive copy of the services list.
        this.services = new ArrayList<>(services);
    }

    public synchronized boolean executeTransaction() {
        List<Service> committedServices = new ArrayList<>();
        // Commit services in order.
        for (Service service : services) {
            System.out.println("Committing service: " + service.getId());
            boolean commitResult;
            // Synchronizing on the service to ensure thread-safe commit.
            synchronized (service) {
                commitResult = service.commit();
            }
            if (!commitResult) {
                System.out.println("Commit failed at service: " + service.getId());
                rollbackCommittedServices(committedServices);
                return false;
            }
            committedServices.add(service);
        }
        System.out.println("All services committed successfully.");
        return true;
    }

    private void rollbackCommittedServices(List<Service> committedServices) {
        // Rollback committed services in reverse order.
        Collections.reverse(committedServices);
        for (Service service : committedServices) {
            boolean rollbackSucceeded = false;
            int retryCount = 0;
            while (retryCount < MAX_ROLLBACK_RETRIES && !rollbackSucceeded) {
                System.out.println("Rolling back service: " + service.getId() + " attempt " + (retryCount + 1));
                synchronized (service) {
                    rollbackSucceeded = service.rollback();
                }
                retryCount++;
            }
            if (!rollbackSucceeded) {
                System.out.println("Rollback failed for service: " + service.getId() + " after " + MAX_ROLLBACK_RETRIES + " attempts");
            }
        }
    }
}