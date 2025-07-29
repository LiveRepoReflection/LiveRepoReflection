package conflictresolution

import (
    "reflect"
    "testing"
)

func TestResolveConflicts(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            result := ResolveConflicts(tc.transactions, tc.numNodes)
            if !reflect.DeepEqual(result, tc.expected) {
                t.Errorf("ResolveConflicts(%v, %d) = %v, want %v",
                    tc.transactions, tc.numNodes, result, tc.expected)
            }
        })
    }
}

// Benchmark tests
func BenchmarkResolveConflicts(b *testing.B) {
    // Create a large test case
    largeTest := []Transaction{
        {
            ID: 1,
            Operations: []Operation{
                {NodeID: 0, Key: "x", Value: "10", OpType: "WRITE"},
                {NodeID: 1, Key: "y", Value: "10", OpType: "WRITE"},
            },
        },
        {
            ID: 2,
            Operations: []Operation{
                {NodeID: 0, Key: "x", Value: "20", OpType: "WRITE"},
                {NodeID: 1, Key: "z", Value: "20", OpType: "WRITE"},
            },
        },
    }

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        ResolveConflicts(largeTest, 2)
    }
}