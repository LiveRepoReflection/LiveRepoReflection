package networkflow

import "testing"

func TestMaximumSatisfiedRequests(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            got := MaximumSatisfiedRequests(tc.n, tc.capacities, tc.nodeCapacities, tc.requests)
            if got != tc.expected {
                t.Errorf("MaximumSatisfiedRequests(%d, %v, %v, %v) = %d, want %d",
                    tc.n, tc.capacities, tc.nodeCapacities, tc.requests, got, tc.expected)
            }
        })
    }
}

func BenchmarkMaximumSatisfiedRequests(b *testing.B) {
    if testing.Short() {
        b.Skip("skipping benchmark in short mode.")
    }
    for i := 0; i < b.N; i++ {
        for _, tc := range testCases {
            MaximumSatisfiedRequests(tc.n, tc.capacities, tc.nodeCapacities, tc.requests)
        }
    }
}