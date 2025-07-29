package distributed_tx;

import java.util.Map;
import java.util.HashMap;

public class TransactionCoordinator {
    private Map<String, BankBranch> branchMap;
    private long timeoutMillis = 2000;

    public TransactionCoordinator() {
        branchMap = new HashMap<>();
    }

    public void registerBranch(BankBranch branch) {
        branchMap.put(branch.getBranchId(), branch);
    }

    private String extractBranchId(String accountId) {
        int index = accountId.indexOf("_");
        if(index > 0) {
            return accountId.substring(0, index);
        }
        return accountId;
    }

    public boolean processTransaction(Transaction tx) {
        String sourceBranchId = extractBranchId(tx.getSourceAccountId());
        String destBranchId = extractBranchId(tx.getDestinationAccountId());

        BankBranch sourceBranch = branchMap.get(sourceBranchId);
        BankBranch destBranch = branchMap.get(destBranchId);

        if (sourceBranch == null || destBranch == null) {
            return false;
        }

        boolean sourceVote = false;
        boolean destVote = false;
        long startTime = System.currentTimeMillis();

        try {
            sourceVote = sourceBranch.prepare(tx);
            destVote = true;
            if (!sourceBranchId.equals(destBranchId)) {
                destVote = destBranch.prepare(tx);
            }
        } catch (Exception e) {
            sourceVote = false;
            destVote = false;
        }
        long elapsed = System.currentTimeMillis() - startTime;
        if (elapsed > timeoutMillis) {
            sourceVote = false;
            destVote = false;
        }

        if (sourceVote && destVote) {
            sourceBranch.commit(tx);
            if (!sourceBranchId.equals(destBranchId)) {
                destBranch.commit(tx);
            }
            return true;
        } else {
            if (sourceVote) {
                sourceBranch.abort(tx);
            }
            if (destVote && !sourceBranchId.equals(destBranchId)) {
                destBranch.abort(tx);
            }
            return false;
        }
    }
}