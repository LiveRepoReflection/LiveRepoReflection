package consensus_log

// LogEntry represents a single entry in the consensus log
type LogEntry struct {
    Term int
    Data string
}

// ReplicationResult represents the result of attempting to replicate logs to a follower
type ReplicationResult struct {
    StartIndex   int
    Entries      []LogEntry
    Success      bool
    LeaderCommit int
}

// ReplicateLogs implements the log replication logic for the Raft consensus algorithm
func ReplicateLogs(leaderLog []LogEntry, followerLogs [][]LogEntry, lastApplied []int, commitIndex int) []ReplicationResult {
    // Handle nil or empty inputs
    if len(followerLogs) == 0 || len(lastApplied) == 0 {
        return []ReplicationResult{}
    }

    // Ensure lastApplied length matches followerLogs length
    if len(lastApplied) > len(followerLogs) {
        lastApplied = lastApplied[:len(followerLogs)]
    }

    results := make([]ReplicationResult, len(followerLogs))

    // Process each follower
    for i, followerLog := range followerLogs {
        results[i] = replicateToFollower(leaderLog, followerLog, lastApplied[i], commitIndex)
    }

    return results
}

// replicateToFollower handles log replication for a single follower
func replicateToFollower(leaderLog []LogEntry, followerLog []LogEntry, lastApplied int, commitIndex int) ReplicationResult {
    // Handle corrupted lastApplied
    if lastApplied >= len(followerLog) {
        lastApplied = len(followerLog) - 1
        if lastApplied < 0 {
            lastApplied = 0
        }
    }

    // If leader log is empty, nothing to replicate
    if len(leaderLog) == 0 {
        return ReplicationResult{
            StartIndex:   0,
            Entries:      []LogEntry{},
            Success:      true,
            LeaderCommit: commitIndex,
        }
    }

    // Find the last matching index between leader and follower logs
    startIndex := findLastMatchingIndex(leaderLog, followerLog)

    // Prepare entries to send
    var entriesToSend []LogEntry
    if startIndex < len(leaderLog) {
        entriesToSend = make([]LogEntry, len(leaderLog)-startIndex)
        copy(entriesToSend, leaderLog[startIndex:])
    }

    return ReplicationResult{
        StartIndex:   startIndex,
        Entries:      entriesToSend,
        Success:      true,
        LeaderCommit: commitIndex,
    }
}

// findLastMatchingIndex finds the last index where leader and follower logs match
func findLastMatchingIndex(leaderLog []LogEntry, followerLog []LogEntry) int {
    // If follower log is empty, start from beginning
    if len(followerLog) == 0 {
        return 0
    }

    // Start from the end of the follower log and work backwards
    minLen := min(len(leaderLog), len(followerLog))
    lastMatchingIndex := 0

    for i := 0; i < minLen; i++ {
        if !logsMatch(leaderLog[i], followerLog[i]) {
            return i
        }
        lastMatchingIndex = i + 1
    }

    return lastMatchingIndex
}

// logsMatch checks if two log entries match in term and data
func logsMatch(leader, follower LogEntry) bool {
    return leader.Term == follower.Term && leader.Data == follower.Data
}

// min returns the minimum of two integers
func min(a, b int) int {
    if a < b {
        return a
    }
    return b
}