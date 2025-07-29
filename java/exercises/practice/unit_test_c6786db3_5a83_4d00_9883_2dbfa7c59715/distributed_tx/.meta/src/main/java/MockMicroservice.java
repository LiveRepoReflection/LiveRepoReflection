import java.util.UUID;

public class MockMicroservice {
    private final int serviceId;

    public MockMicroservice(int serviceId) {
        this.serviceId = serviceId;
    }

    //Simulates calling the microservice
    public void executeTransaction(UUID transactionId, String operationData) {
        // Simulate some work and potential failure
        try {
            Thread.sleep((long)(Math.random() * 100)); // Simulate variable execution time
            if (Math.random() < 0.1) { // Simulate a 10% chance of failure
                throw new RuntimeException("Service " + serviceId + " failed to execute transaction " + transactionId);
            }
            System.out.println("Service " + serviceId + " executed transaction " + transactionId + " with data: " + operationData);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Service " + serviceId + " interrupted during transaction " + transactionId, e);
        }
    }

    public void rollbackTransaction(UUID transactionId) {
        // Simulate rollback
        try {
            Thread.sleep((long)(Math.random() * 50)); // Simulate variable rollback time
            System.out.println("Service " + serviceId + " rolled back transaction " + transactionId);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new RuntimeException("Service " + serviceId + " interrupted during rollback of transaction " + transactionId, e);
        }
    }
}