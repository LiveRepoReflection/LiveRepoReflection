package distributed_tx;

import java.util.*;
import java.util.concurrent.*;

public class DistributedTransactionManager {
    private final Map<String, Service> serviceMap;
    private final long timeoutMillis = 500;
    private final int commitRetryLimit = 3;
    private final int rollbackRetryLimit = 3;
    private final ExecutorService executor;

    public DistributedTransactionManager(List<Service> services) {
        serviceMap = new ConcurrentHashMap<>();
        for (Service s : services) {
            serviceMap.put(s.getName(), s);
        }
        executor = Executors.newCachedThreadPool();
    }

    public boolean executeTransaction(List<Operation> operations) {
        TransactionContext txContext = new TransactionContext();
        System.out.println("Starting transaction: " + txContext.getTransactionId());

        // Phase 1: Prepare
        for (Operation op : operations) {
            Service service = serviceMap.get(op.getServiceName());
            if (service == null) {
                System.out.println("Service not found for operation on: " + op.getServiceName());
                rollbackAll(txContext, operations);
                return false;
            }
            System.out.println("Preparing operation on service: " + service.getName());
            Future<Boolean> future = executor.submit(() -> service.prepare(txContext, op.getOperationDetails()));
            try {
                boolean prepared = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                if (!prepared) {
                    System.out.println("Service " + service.getName() + " failed to prepare.");
                    rollbackAll(txContext, operations);
                    return false;
                }
            } catch (TimeoutException te) {
                System.out.println("Timeout during prepare on service: " + service.getName());
                rollbackAll(txContext, operations);
                return false;
            } catch (Exception e) {
                System.out.println("Exception during prepare on service: " + service.getName());
                rollbackAll(txContext, operations);
                return false;
            }
        }

        // Phase 2: Commit
        System.out.println("All services prepared successfully. Committing transaction: " + txContext.getTransactionId());
        boolean commitSuccess = true;
        for (Operation op : operations) {
            Service service = serviceMap.get(op.getServiceName());
            if (service == null)
                continue;
            int attempts = 0;
            boolean committed = false;
            while (attempts < commitRetryLimit && !committed) {
                System.out.println("Attempt " + (attempts + 1) + " to commit on service: " + service.getName());
                Future<Boolean> future = executor.submit(() -> service.commit(txContext, op.getOperationDetails()));
                try {
                    committed = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                } catch (TimeoutException te) {
                    System.out.println("Timeout during commit on service: " + service.getName());
                    committed = false;
                } catch (Exception e) {
                    System.out.println("Exception during commit on service: " + service.getName());
                    committed = false;
                }
                attempts++;
            }
            if (!committed) {
                System.out.println("Service " + service.getName() + " failed to commit after retries.");
                commitSuccess = false;
            }
        }

        if (!commitSuccess) {
            rollbackAll(txContext, operations);
            System.out.println("Transaction " + txContext.getTransactionId() + " failed to commit; rolled back.");
            return false;
        }

        System.out.println("Transaction " + txContext.getTransactionId() + " committed successfully.");
        return true;
    }

    private void rollbackAll(TransactionContext txContext, List<Operation> operations) {
        System.out.println("Rolling back transaction: " + txContext.getTransactionId());
        for (Operation op : operations) {
            Service service = serviceMap.get(op.getServiceName());
            if (service == null)
                continue;
            int attempts = 0;
            boolean rolledBack = false;
            while (attempts < rollbackRetryLimit && !rolledBack) {
                System.out.println("Attempt " + (attempts + 1) + " to rollback on service: " + service.getName());
                Future<Boolean> future = executor.submit(() -> service.rollback(txContext, op.getOperationDetails()));
                try {
                    rolledBack = future.get(timeoutMillis, TimeUnit.MILLISECONDS);
                } catch (TimeoutException te) {
                    System.out.println("Timeout during rollback on service: " + service.getName());
                    rolledBack = false;
                } catch (Exception e) {
                    System.out.println("Exception during rollback on service: " + service.getName());
                    rolledBack = false;
                }
                attempts++;
            }
            if (!rolledBack) {
                System.out.println("Service " + service.getName() + " failed to rollback after retries.");
            }
        }
    }

    public void shutdown() {
        executor.shutdown();
    }
}