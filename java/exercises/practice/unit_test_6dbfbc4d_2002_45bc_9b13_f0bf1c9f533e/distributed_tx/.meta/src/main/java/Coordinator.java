import java.util.*;
import java.util.concurrent.*;

public class Coordinator {
    private final long prepareTimeoutMs;
    private final ConcurrentHashMap<String, List<Service>> transactionMap = new ConcurrentHashMap<>();
    private final ExecutorService executorService = Executors.newCachedThreadPool();

    public Coordinator(long prepareTimeoutMs) {
        this.prepareTimeoutMs = prepareTimeoutMs;
    }

    public String beginTransaction() {
        String transactionId = UUID.randomUUID().toString();
        transactionMap.put(transactionId, new CopyOnWriteArrayList<>());
        return transactionId;
    }

    public void registerService(Service service, String transactionId) {
        List<Service> services = transactionMap.get(transactionId);
        if (services == null) {
            throw new IllegalArgumentException("Transaction id not found: " + transactionId);
        }
        services.add(service);
    }

    public boolean prepareTransaction(String transactionId) {
        List<Service> services = transactionMap.get(transactionId);
        if (services == null || services.isEmpty()) {
            return false;
        }
        
        List<Future<Boolean>> futures = new ArrayList<>();
        for (Service service : services) {
            Future<Boolean> future = executorService.submit(() -> service.prepare(transactionId));
            futures.add(future);
        }
        
        boolean allPrepared = true;
        for (Future<Boolean> future : futures) {
            try {
                boolean result = future.get(prepareTimeoutMs, TimeUnit.MILLISECONDS);
                if (!result) {
                    allPrepared = false;
                    break;
                }
            } catch (TimeoutException | InterruptedException | ExecutionException e) {
                allPrepared = false;
                break;
            }
        }
        return allPrepared;
    }

    public void commitTransaction(String transactionId) {
        List<Service> services = transactionMap.get(transactionId);
        if (services != null) {
            for (Service service : services) {
                service.commit(transactionId);
            }
            transactionMap.remove(transactionId);
        }
    }

    public void rollbackTransaction(String transactionId) {
        List<Service> services = transactionMap.get(transactionId);
        if (services != null) {
            for (Service service : services) {
                service.rollback(transactionId);
            }
            transactionMap.remove(transactionId);
        }
    }
}