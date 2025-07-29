package dynamic_routing

import (
	"testing"
)

func TestRoutingSystem(t *testing.T) {
	tests := []struct {
		name           string
		edges          [][3]int
		nodeCount      int
		operations     []struct {
			opType   string // "Route" or "UpdateLatency"
			args     [2]int // For Route: [start, end], For UpdateLatency: [u, v]
			latency  int    // Only for UpdateLatency
			expected int    // Expected result for Route
		}
	}{
		{
			name:      "Basic routing",
			nodeCount: 3,
			edges:     [][3]int{{1, 2, 5}, {2, 3, 2}, {1, 3, 10}},
			operations: []struct {
				opType   string
				args     [2]int
				latency  int
				expected int
			}{
				{opType: "Route", args: [2]int{1, 3}, expected: 7},
				{opType: "UpdateLatency", args: [2]int{2, 3}, latency: 1},
				{opType: "Route", args: [2]int{1, 3}, expected: 6},
				{opType: "UpdateLatency", args: [2]int{1, 2}, latency: 1},
				{opType: "Route", args: [2]int{1, 3}, expected: 2},
			},
		},
		{
			name:      "Disconnected graph",
			nodeCount: 4,
			edges:     [][3]int{{1, 2, 3}, {3, 4, 2}},
			operations: []struct {
				opType   string
				args     [2]int
				latency  int
				expected int
			}{
				{opType: "Route", args: [2]int{1, 4}, expected: -1},
				{opType: "Route", args: [2]int{1, 2}, expected: 3},
			},
		},
		{
			name:      "Multiple edges between nodes",
			nodeCount: 3,
			edges:     [][3]int{{1, 2, 5}, {1, 2, 3}, {2, 3, 2}},
			operations: []struct {
				opType   string
				args     [2]int
				latency  int
				expected int
			}{
				{opType: "Route", args: [2]int{1, 3}, expected: 5},
				{opType: "UpdateLatency", args: [2]int{1, 2}, latency: 1},
				{opType: "Route", args: [2]int{1, 3}, expected: 3},
			},
		},
		{
			name:      "Large latency values",
			nodeCount: 3,
			edges:     [][3]int{{1, 2, 10000}, {2, 3, 10000}},
			operations: []struct {
				opType   string
				args     [2]int
				latency  int
				expected int
			}{
				{opType: "Route", args: [2]int{1, 3}, expected: 20000},
				{opType: "UpdateLatency", args: [2]int{2, 3}, latency: 1},
				{opType: "Route", args: [2]int{1, 3}, expected: 10001},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			rs := NewRoutingSystem(tt.nodeCount, tt.edges)
			for _, op := range tt.operations {
				switch op.opType {
				case "Route":
					result := rs.Route(op.args[0], op.args[1])
					if result != op.expected {
						t.Errorf("Route(%d, %d) = %d, want %d", op.args[0], op.args[1], result, op.expected)
					}
				case "UpdateLatency":
					rs.UpdateLatency(op.args[0], op.args[1], op.latency)
				}
			}
		})
	}
}