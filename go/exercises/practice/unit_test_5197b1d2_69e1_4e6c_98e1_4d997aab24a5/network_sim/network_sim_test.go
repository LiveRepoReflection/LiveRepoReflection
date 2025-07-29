package network_sim

import (
	"math/rand"
	"testing"
	"time"
)

func TestNetworkSimulator(t *testing.T) {
	rand.Seed(time.Now().UnixNano())

	tests := []struct {
		name                 string
		n                    int
		nodeCapacities       []int
		failureProbabilities []float64
		downtime             int
		networkBandwidth     int
		networkLatency       int
		messages             []Message
		simulationDuration   int
	}{
		{
			name:                 "basic_test",
			n:                    3,
			nodeCapacities:       []int{100, 150, 200},
			failureProbabilities: []float64{0.1, 0.05, 0.0},
			downtime:             2,
			networkBandwidth:     500,
			networkLatency:       1,
			messages: []Message{
				{Source: 0, Destination: 2, Size: 50, CreationTime: 0},
				{Source: 1, Destination: 0, Size: 75, CreationTime: 1},
			},
			simulationDuration: 5,
		},
		{
			name:                 "high_failure_rate",
			n:                    5,
			nodeCapacities:       []int{200, 200, 200, 200, 200},
			failureProbabilities: []float64{0.5, 0.5, 0.5, 0.5, 0.5},
			downtime:             3,
			networkBandwidth:     1000,
			networkLatency:       2,
			messages: []Message{
				{Source: 0, Destination: 4, Size: 100, CreationTime: 0},
				{Source: 1, Destination: 3, Size: 150, CreationTime: 1},
				{Source: 2, Destination: 1, Size: 200, CreationTime: 2},
			},
			simulationDuration: 10,
		},
		{
			name:                 "bandwidth_constrained",
			n:                    4,
			nodeCapacities:       []int{300, 300, 300, 300},
			failureProbabilities: []float64{0.0, 0.0, 0.0, 0.0},
			downtime:             1,
			networkBandwidth:     100,
			networkLatency:       1,
			messages: []Message{
				{Source: 0, Destination: 1, Size: 60, CreationTime: 0},
				{Source: 1, Destination: 2, Size: 60, CreationTime: 0},
				{Source: 2, Destination: 3, Size: 60, CreationTime: 0},
			},
			simulationDuration: 5,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			latencies := SimulateNetwork(
				tt.n,
				tt.nodeCapacities,
				tt.failureProbabilities,
				tt.downtime,
				tt.networkBandwidth,
				tt.networkLatency,
				tt.messages,
				tt.simulationDuration,
			)

			if len(latencies) > len(tt.messages) {
				t.Errorf("got %d latencies, expected <= %d messages", len(latencies), len(tt.messages))
			}

			for _, latency := range latencies {
				if latency == -1 {
					continue
				}
				if latency < 0 || latency > float64(tt.simulationDuration) {
					t.Errorf("latency %f outside valid range [0, %d]", latency, tt.simulationDuration)
				}
			}
		})
	}
}

func BenchmarkNetworkSimulator(b *testing.B) {
	n := 100
	nodeCapacities := make([]int, n)
	failureProbabilities := make([]float64, n)
	messages := make([]Message, 1000)

	for i := 0; i < n; i++ {
		nodeCapacities[i] = 100 + rand.Intn(900)
		failureProbabilities[i] = rand.Float64() * 0.2
	}

	for i := 0; i < 1000; i++ {
		messages[i] = Message{
			Source:        rand.Intn(n),
			Destination:   rand.Intn(n),
			Size:          10 + rand.Intn(490),
			CreationTime:  rand.Intn(100),
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		SimulateNetwork(
			n,
			nodeCapacities,
			failureProbabilities,
			2,
			10000,
			2,
			messages,
			100,
		)
	}
}