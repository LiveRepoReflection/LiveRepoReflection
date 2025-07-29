import java.util.Map;

public class Proposal {
    public final int proposalId;
    public final int proposerId;
    public final ActionType actionType;
    public final String actionDetails;
    public final Map<Integer, Boolean> votes;
    public final long startTimestamp;
    public final long endTimestamp;

    public Proposal(int proposalId, int proposerId, ActionType actionType, String actionDetails,
                  Map<Integer, Boolean> votes, long startTimestamp, long endTimestamp) {
        this.proposalId = proposalId;
        this.proposerId = proposerId;
        this.actionType = actionType;
        this.actionDetails = actionDetails;
        this.votes = votes;
        this.startTimestamp = startTimestamp;
        this.endTimestamp = endTimestamp;
    }
}