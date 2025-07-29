public class ServiceExecutor {
    public boolean execute(String serviceId, String operationData) {
        // Simulate service execution
        if (operationData.contains("fail:true")) {
            return false;
        }
        System.out.println("Executing " + serviceId + " with data: " + operationData);
        return true;
    }

    public boolean compensate(String serviceId, String compensationData) {
        System.out.println("Compensating " + serviceId + " with data: " + compensationData);
        return true;
    }
}