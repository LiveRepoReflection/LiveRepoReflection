package net_routing

import (
	"math"
	"testing"
)

func TestNetworkRouting(t *testing.T) {
	tests := []struct {
		name          string
		initialConn   []Connection
		operations    []Operation
		queries       []PathQuery
		expectedPaths []PathResult
	}{
		{
			name: "Basic network with static connections",
			initialConn: []Connection{
				{1, 2, 10},
				{2, 3, 5},
				{3, 4, 7},
			},
			operations: []Operation{},
			queries: []PathQuery{
				{1, 4},
				{2, 4},
				{1, 3},
			},
			expectedPaths: []PathResult{
				{[]int{1, 2, 3, 4}, 22},
				{[]int{2, 3, 4}, 12},
				{[]int{1, 2, 3}, 15},
			},
		},
		{
			name: "Dynamic network with node additions",
			initialConn: []Connection{
				{1, 2, 5},
				{2, 3, 10},
			},
			operations: []Operation{
				{Type: "AddNode", NodeID: 4},
				{Type: "AddConnection", Node1: 3, Node2: 4, Latency: 3},
			},
			queries: []PathQuery{
				{1, 4},
				{2, 4},
			},
			expectedPaths: []PathResult{
				{[]int{1, 2, 3, 4}, 18},
				{[]int{2, 3, 4}, 13},
			},
		},
		{
			name: "Network with node removal",
			initialConn: []Connection{
				{1, 2, 5},
				{2, 3, 10},
				{3, 4, 7},
				{1, 4, 20},
			},
			operations: []Operation{
				{Type: "RemoveNode", NodeID: 3},
			},
			queries: []PathQuery{
				{1, 4},
				{2, 4},
			},
			expectedPaths: []PathResult{
				{[]int{1, 4}, 20},
				{[]int{2, 1, 4}, 25},
			},
		},
		{
			name: "Unreachable nodes",
			initialConn: []Connection{
				{1, 2, 5},
				{3, 4, 10},
			},
			operations: []Operation{},
			queries: []PathQuery{
				{1, 3},
				{2, 4},
			},
			expectedPaths: []PathResult{
				{[]int{}, math.MaxInt32},
				{[]int{}, math.MaxInt32},
			},
		},
		{
			name: "Multiple shortest paths with different latencies",
			initialConn: []Connection{
				{1, 2, 5},
				{2, 3, 5},
				{1, 3, 15},
				{3, 4, 5},
				{2, 4, 15},
			},
			operations: []Operation{},
			queries: []PathQuery{
				{1, 4},
			},
			expectedPaths: []PathResult{
				{[]int{1, 2, 3, 4}, 15},
			},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			net := NewNetwork()
			
			// Initialize network
			for _, conn := range tt.initialConn {
				net.AddConnection(conn.Node1, conn.Node2, conn.Latency)
			}
			
			// Apply operations
			for _, op := range tt.operations {
				switch op.Type {
				case "AddNode":
					net.AddNode(op.NodeID)
				case "RemoveNode":
					net.RemoveNode(op.NodeID)
				case "AddConnection":
					net.AddConnection(op.Node1, op.Node2, op.Latency)
				case "RemoveConnection":
					net.RemoveConnection(op.Node1, op.Node2)
				}
			}
			
			// Test queries
			for i, query := range tt.queries {
				path, latency := net.GetPath(query.From, query.To)
				expected := tt.expectedPaths[i]
				
				if !equalPaths(path, expected.Path) || latency != expected.Latency {
					t.Errorf("Query %d (%d->%d) failed:\nExpected: %v (latency: %d)\nGot: %v (latency: %d)",
						i+1, query.From, query.To, expected.Path, expected.Latency, path, latency)
				}
			}
		})
	}
}

func equalPaths(a, b []int) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}