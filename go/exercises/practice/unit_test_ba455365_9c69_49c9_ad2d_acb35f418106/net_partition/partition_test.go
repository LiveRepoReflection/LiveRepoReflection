package partition

import (
    "testing"
)

func TestOptimalPartition(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            got := OptimalPartition(tc.n, tc.k, tc.serviceCosts, tc.edges, tc.maxClusterSize, tc.maxInterClusterLatency)
            if got != tc.expected {
                t.Errorf("OptimalPartition(%d, %d, %v, %v, %d, %d) = %d; want %d",
                    tc.n, tc.k, tc.serviceCosts, tc.edges, tc.maxClusterSize, tc.maxInterClusterLatency,
                    got, tc.expected)
            }
        })
    }
}

func BenchmarkOptimalPartition(b *testing.B) {
    // Benchmark with the complex case
    tc := testCases[5]
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        OptimalPartition(tc.n, tc.k, tc.serviceCosts, tc.edges, tc.maxClusterSize, tc.maxInterClusterLatency)
    }
}

// Additional test for edge cases
func TestOptimalPartitionEdgeCases(t *testing.T) {
    tests := []struct {
        description           string
        n                    int
        k                    int
        serviceCosts         []int
        edges                [][]int
        maxClusterSize       int
        maxInterClusterLatency int
        expected             int
    }{
        {
            description: "empty graph",
            n: 5,
            k: 5,
            serviceCosts: []int{1, 1, 1, 1, 1},
            edges: [][]int{},
            maxClusterSize: 1,
            maxInterClusterLatency: 100,
            expected: 5,
        },
        {
            description: "single cluster for all nodes",
            n: 4,
            k: 1,
            serviceCosts: []int{1, 2, 3, 4},
            edges: [][]int{{0, 1, 1}, {1, 2, 1}, {2, 3, 1}},
            maxClusterSize: 4,
            maxInterClusterLatency: 0,
            expected: 10,
        },
        {
            description: "each node in its own cluster",
            n: 3,
            k: 3,
            serviceCosts: []int{1, 2, 3},
            edges: [][]int{{0, 1, 1}, {1, 2, 1}},
            maxClusterSize: 1,
            maxInterClusterLatency: 2,
            expected: 6,
        },
    }

    for _, tt := range tests {
        t.Run(tt.description, func(t *testing.T) {
            got := OptimalPartition(tt.n, tt.k, tt.serviceCosts, tt.edges, tt.maxClusterSize, tt.maxInterClusterLatency)
            if got != tt.expected {
                t.Errorf("OptimalPartition(%d, %d, %v, %v, %d, %d) = %d; want %d",
                    tt.n, tt.k, tt.serviceCosts, tt.edges, tt.maxClusterSize, tt.maxInterClusterLatency,
                    got, tt.expected)
            }
        })
    }
}