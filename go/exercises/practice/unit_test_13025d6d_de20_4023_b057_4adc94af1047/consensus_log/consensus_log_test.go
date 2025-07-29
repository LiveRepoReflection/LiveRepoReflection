package consensus_log

import (
    "reflect"
    "testing"
)

func TestReplicateLogs(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            result := ReplicateLogs(tc.leaderLog, tc.followerLogs, tc.lastApplied, tc.commitIndex)
            
            if len(result) != len(tc.expected) {
                t.Fatalf("Expected %d results, got %d", len(tc.expected), len(result))
            }

            for i := range result {
                if !reflect.DeepEqual(result[i], tc.expected[i]) {
                    t.Errorf("For follower %d:\nexpected: %+v\ngot: %+v", 
                        i, tc.expected[i], result[i])
                }
            }
        })
    }
}

func TestEdgeCases(t *testing.T) {
    // Test nil inputs
    result := ReplicateLogs(nil, nil, nil, 0)
    if len(result) != 0 {
        t.Errorf("Expected empty result for nil inputs, got %v", result)
    }

    // Test mismatched lengths
    result = ReplicateLogs(
        []LogEntry{{Term: 1, Data: "cmd"}},
        [][]LogEntry{{}},
        []int{0, 0}, // More lastApplied than followerLogs
        0,
    )
    if len(result) != 1 {
        t.Errorf("Expected result length 1, got %d", len(result))
    }
}

func BenchmarkReplicateLogs(b *testing.B) {
    leaderLog := []LogEntry{
        {Term: 1, Data: "cmd1"},
        {Term: 1, Data: "cmd2"},
        {Term: 2, Data: "cmd3"},
        {Term: 2, Data: "cmd4"},
        {Term: 3, Data: "cmd5"},
    }
    
    followerLogs := [][]LogEntry{
        {
            {Term: 1, Data: "cmd1"},
            {Term: 1, Data: "cmd2"},
        },
        {
            {Term: 1, Data: "cmd1"},
        },
    }
    
    lastApplied := []int{1, 0}
    commitIndex := 4

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        ReplicateLogs(leaderLog, followerLogs, lastApplied, commitIndex)
    }
}