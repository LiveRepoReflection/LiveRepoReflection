package distributed_tx;

import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.ReentrantLock;

public class TransactionManager {
    private final Map<Integer, Service> services;
    private final long LOCK_TIMEOUT_MS = 100;

    public TransactionManager() {
        services = new HashMap<>();
        Random rand = new Random();
        for (int i = 1; i <= 5; i++) {
            int initial = rand.nextInt(51) + 50;
            services.put(i, new Service(i, initial));
            System.out.println("Initialized Service " + i + " with resource: " + initial);
        }
    }

    public Service getService(int id) {
        return services.get(id);
    }

    public void setServiceResource(int id, int value) {
        Service s = services.get(id);
        if (s != null) {
            s.setResource(value);
        }
    }

    // Executes a transaction using the two-phase commit protocol.
    // Returns true if the transaction is committed successfully, false if aborted.
    public boolean executeTransaction(List<TransactionOperation> ops) {
        Map<Integer, List<TransactionOperation>> serviceOps = new HashMap<>();
        List<Integer> serviceOrder = new ArrayList<>();
        for (TransactionOperation op : ops) {
            serviceOps.computeIfAbsent(op.getServiceId(), k -> {
                serviceOrder.add(k);
                return new ArrayList<>();
            }).add(op);
        }

        List<Service> lockedServices = new ArrayList<>();
        try {
            for (Integer serviceId : serviceOrder) {
                Service service = services.get(serviceId);
                if (service == null) {
                    System.out.println("Service " + serviceId + " not found. Aborting transaction.");
                    releaseLocks(lockedServices);
                    return false;
                }
                ReentrantLock lock = service.getLock();
                if (!lock.tryLock(LOCK_TIMEOUT_MS, TimeUnit.MILLISECONDS)) {
                    System.out.println("Failed to acquire lock on Service " + serviceId + ". Potential deadlock detected. Aborting transaction.");
                    releaseLocks(lockedServices);
                    return false;
                }
                lockedServices.add(service);
            }

            for (Service service : lockedServices) {
                List<TransactionOperation> opsForService = serviceOps.get(service.getId());
                if (opsForService != null) {
                    boolean vote = service.prepare(opsForService);
                    if (!vote) {
                        System.out.println("Service " + service.getId() + " voted abort. Rolling back transaction.");
                        for (Service s : lockedServices) {
                            s.rollback();
                        }
                        return false;
                    }
                }
            }

            for (Service service : lockedServices) {
                service.commit();
            }
            System.out.println("Transaction committed successfully.");
            return true;
        } catch (InterruptedException e) {
            System.out.println("Transaction interrupted. Rolling back.");
            for (Service s : lockedServices) {
                s.rollback();
            }
            Thread.currentThread().interrupt();
            return false;
        } finally {
            releaseLocks(lockedServices);
        }
    }

    private void releaseLocks(List<Service> servicesLocked) {
        for (Service service : servicesLocked) {
            ReentrantLock lock = service.getLock();
            if (lock.isHeldByCurrentThread()) {
                lock.unlock();
            }
        }
    }
}