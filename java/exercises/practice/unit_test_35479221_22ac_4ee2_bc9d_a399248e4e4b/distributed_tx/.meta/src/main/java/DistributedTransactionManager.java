package distributed_tx;

import java.util.List;

public class DistributedTransactionManager {
    public boolean processTransaction(List<TransactionalResource> resources) {
        boolean allPrepared = true;
        // Phase 1: Prepare all resources.
        for (TransactionalResource resource : resources) {
            if (!resource.prepare()) {
                allPrepared = false;
            }
        }
        // Phase 2: Commit if all resources successfully prepared; otherwise, rollback all.
        if (allPrepared) {
            for (TransactionalResource resource : resources) {
                resource.commit();
            }
            return true;
        } else {
            for (TransactionalResource resource : resources) {
                resource.rollback();
            }
            return false;
        }
    }
}