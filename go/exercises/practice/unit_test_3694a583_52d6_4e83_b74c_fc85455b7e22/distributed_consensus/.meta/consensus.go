package consensus

func DecideConsensus(N int, proposals []bool) bool {
    if N == 1 {
        return proposals[0]
    }

    // Count total commit proposals
    totalCommit := 0
    for _, p := range proposals {
        if p {
            totalCommit++
        }
    }

    // Each node votes commit only if all proposals were commit
    // So total commit votes equals number of nodes where proposals[i] && (totalCommit == N)
    var commitVotes int
    if totalCommit == N {
        commitVotes = N
    } else {
        commitVotes = 0
    }

    // Majority decision
    return commitVotes > N/2
}