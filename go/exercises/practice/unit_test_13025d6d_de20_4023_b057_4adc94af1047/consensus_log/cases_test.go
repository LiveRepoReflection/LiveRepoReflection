package consensus_log

var testCases = []struct {
    description   string
    leaderLog    []LogEntry
    followerLogs [][]LogEntry
    lastApplied  []int
    commitIndex  int
    expected     []ReplicationResult
}{
    {
        description: "empty logs",
        leaderLog:   []LogEntry{},
        followerLogs: [][]LogEntry{
            {},
            {},
        },
        lastApplied: []int{0, 0},
        commitIndex: 0,
        expected: []ReplicationResult{
            {StartIndex: 0, Entries: []LogEntry{}, Success: true, LeaderCommit: 0},
            {StartIndex: 0, Entries: []LogEntry{}, Success: true, LeaderCommit: 0},
        },
    },
    {
        description: "simple replication with matching logs",
        leaderLog: []LogEntry{
            {Term: 1, Data: "cmd1"},
            {Term: 1, Data: "cmd2"},
            {Term: 1, Data: "cmd3"},
        },
        followerLogs: [][]LogEntry{
            {
                {Term: 1, Data: "cmd1"},
                {Term: 1, Data: "cmd2"},
            },
        },
        lastApplied: []int{1},
        commitIndex: 2,
        expected: []ReplicationResult{
            {
                StartIndex: 2,
                Entries:   []LogEntry{{Term: 1, Data: "cmd3"}},
                Success:   true,
                LeaderCommit: 2,
            },
        },
    },
    {
        description: "conflicting entries",
        leaderLog: []LogEntry{
            {Term: 1, Data: "cmd1"},
            {Term: 2, Data: "cmd2"},
            {Term: 2, Data: "cmd3"},
        },
        followerLogs: [][]LogEntry{
            {
                {Term: 1, Data: "cmd1"},
                {Term: 1, Data: "different_cmd"},
            },
        },
        lastApplied: []int{1},
        commitIndex: 2,
        expected: []ReplicationResult{
            {
                StartIndex: 1,
                Entries: []LogEntry{
                    {Term: 2, Data: "cmd2"},
                    {Term: 2, Data: "cmd3"},
                },
                Success:      true,
                LeaderCommit: 2,
            },
        },
    },
    {
        description: "corrupted lastApplied",
        leaderLog: []LogEntry{
            {Term: 1, Data: "cmd1"},
            {Term: 1, Data: "cmd2"},
        },
        followerLogs: [][]LogEntry{
            {
                {Term: 1, Data: "cmd1"},
            },
        },
        lastApplied: []int{5}, // corrupted: larger than log length
        commitIndex: 1,
        expected: []ReplicationResult{
            {
                StartIndex: 1,
                Entries:   []LogEntry{{Term: 1, Data: "cmd2"}},
                Success:   true,
                LeaderCommit: 1,
            },
        },
    },
    {
        description: "completely different logs",
        leaderLog: []LogEntry{
            {Term: 3, Data: "cmd1"},
            {Term: 3, Data: "cmd2"},
        },
        followerLogs: [][]LogEntry{
            {
                {Term: 1, Data: "old_cmd1"},
                {Term: 1, Data: "old_cmd2"},
                {Term: 2, Data: "old_cmd3"},
            },
        },
        lastApplied: []int{2},
        commitIndex: 1,
        expected: []ReplicationResult{
            {
                StartIndex: 0,
                Entries: []LogEntry{
                    {Term: 3, Data: "cmd1"},
                    {Term: 3, Data: "cmd2"},
                },
                Success:      true,
                LeaderCommit: 1,
            },
        },
    },
}