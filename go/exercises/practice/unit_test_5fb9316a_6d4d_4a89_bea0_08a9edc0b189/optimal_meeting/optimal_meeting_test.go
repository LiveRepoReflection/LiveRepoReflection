package optimal_meeting

import "testing"

func TestOptimalMeetingPoint(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            got := OptimalMeetingPoint(tc.graph, tc.friendLocations)
            if got != tc.expected {
                t.Errorf("OptimalMeetingPoint(%v, %v) = %d; want %d", 
                    tc.graph, tc.friendLocations, got, tc.expected)
            }
        })
    }
}

func BenchmarkOptimalMeetingPoint(b *testing.B) {
    // Use the first test case for benchmarking
    tc := testCases[0]
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        OptimalMeetingPoint(tc.graph, tc.friendLocations)
    }
}