package network_reconstruction

import (
	"testing"
	"time"
)

func TestNetworkReconstruction(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		log      []LogEntry
		expected int
	}{
		{
			name: "empty log",
			n:    5,
			log:  []LogEntry{},
			expected: 0,
		},
		{
			name: "single direct communication",
			n:    5,
			log: []LogEntry{
				{Timestamp: time.Now().Unix(), Source: 0, Destination: 1},
			},
			expected: 1,
		},
		{
			name: "multiple communications same nodes",
			n:    5,
			log: []LogEntry{
				{Timestamp: 1, Source: 0, Destination: 1},
				{Timestamp: 2, Source: 0, Destination: 1},
				{Timestamp: 3, Source: 0, Destination: 1},
			},
			expected: 1,
		},
		{
			name: "indirect communication chain",
			n:    5,
			log: []LogEntry{
				{Timestamp: 1, Source: 0, Destination: 1},
				{Timestamp: 2, Source: 1, Destination: 2},
				{Timestamp: 3, Source: 0, Destination: 2},
			},
			expected: 2,
		},
		{
			name: "multiple disconnected components",
			n:    6,
			log: []LogEntry{
				{Timestamp: 1, Source: 0, Destination: 1},
				{Timestamp: 2, Source: 1, Destination: 2},
				{Timestamp: 3, Source: 3, Destination: 4},
				{Timestamp: 4, Source: 4, Destination: 5},
			},
			expected: 4,
		},
		{
			name: "invalid node IDs",
			n:    3,
			log: []LogEntry{
				{Timestamp: 1, Source: 0, Destination: 1},
				{Timestamp: 2, Source: 1, Destination: 3}, // invalid
				{Timestamp: 3, Source: 0, Destination: 2},
			},
			expected: 2,
		},
		{
			name: "self-communication",
			n:    3,
			log: []LogEntry{
				{Timestamp: 1, Source: 0, Destination: 0},
				{Timestamp: 2, Source: 0, Destination: 1},
				{Timestamp: 3, Source: 1, Destination: 2},
			},
			expected: 2,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			actual := ReconstructNetwork(tt.n, tt.log)
			if actual != tt.expected {
				t.Errorf("ReconstructNetwork(%d, %v) = %d, expected %d", tt.n, tt.log, actual, tt.expected)
			}
		})
	}
}

func BenchmarkNetworkReconstruction(b *testing.B) {
	n := 1000
	log := make([]LogEntry, 10000)
	for i := 0; i < 10000; i++ {
		log[i] = LogEntry{
			Timestamp:   int64(i),
			Source:      i % n,
			Destination: (i + 1) % n,
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ReconstructNetwork(n, log)
	}
}