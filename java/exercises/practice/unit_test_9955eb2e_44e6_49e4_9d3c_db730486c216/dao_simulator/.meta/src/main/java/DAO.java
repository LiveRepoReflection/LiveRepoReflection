import java.util.Collections;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantLock;

public class DAO {
    private final Set<Integer> members;
    private long treasuryBalance;
    private int quorumPercentage;
    private final ReentrantLock lock = new ReentrantLock();

    public DAO(Set<Integer> initialMembers, long initialTreasury, int initialQuorumPercentage) {
        this.members = Collections.newSetFromMap(new ConcurrentHashMap<>());
        this.members.addAll(initialMembers);
        this.treasuryBalance = initialTreasury;
        this.quorumPercentage = initialQuorumPercentage;
    }

    public boolean submitProposal(Proposal proposal, long currentTimestamp) {
        if (!isValidProposal(proposal, currentTimestamp)) {
            return false;
        }

        lock.lock();
        try {
            if (!processVotes(proposal)) {
                return true; // Proposal processed but failed
            }

            return executeProposal(proposal);
        } finally {
            lock.unlock();
        }
    }

    private boolean isValidProposal(Proposal proposal, long currentTimestamp) {
        return members.contains(proposal.proposerId) &&
               proposal.startTimestamp <= currentTimestamp &&
               proposal.endTimestamp >= currentTimestamp;
    }

    private boolean processVotes(Proposal proposal) {
        Set<Integer> votingMembers = new HashSet<>();
        int yesVotes = 0;

        for (Map.Entry<Integer, Boolean> entry : proposal.votes.entrySet()) {
            if (members.contains(entry.getKey())) {
                votingMembers.add(entry.getKey());
                if (entry.getValue()) {
                    yesVotes++;
                }
            }
        }

        double currentQuorum = (double) yesVotes / members.size() * 100;
        return currentQuorum >= quorumPercentage;
    }

    private boolean executeProposal(Proposal proposal) {
        try {
            switch (proposal.actionType) {
                case TRANSFER_ASSETS:
                    return handleTransfer(proposal.actionDetails);
                case ADD_MEMBER:
                    return handleAddMember(proposal.actionDetails);
                case MODIFY_QUORUM:
                    return handleModifyQuorum(proposal.actionDetails);
                default:
                    return false;
            }
        } catch (Exception e) {
            return false;
        }
    }

    private boolean handleTransfer(String details) {
        String[] parts = details.split(",");
        if (parts.length != 2) return false;

        try {
            int recipientId = Integer.parseInt(parts[0]);
            long amount = Long.parseLong(parts[1]);

            if (!members.contains(recipientId) || amount <= 0 || amount > treasuryBalance) {
                return false;
            }

            treasuryBalance -= amount;
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    private boolean handleAddMember(String details) {
        try {
            int newMemberId = Integer.parseInt(details);
            if (members.contains(newMemberId)) {
                return false;
            }
            members.add(newMemberId);
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    private boolean handleModifyQuorum(String details) {
        try {
            int newQuorum = Integer.parseInt(details);
            if (newQuorum < 0 || newQuorum > 100) {
                return false;
            }
            quorumPercentage = newQuorum;
            return true;
        } catch (NumberFormatException e) {
            return false;
        }
    }

    public long getTreasuryBalance() {
        return treasuryBalance;
    }

    public Set<Integer> getMembers() {
        return new HashSet<>(members);
    }
}