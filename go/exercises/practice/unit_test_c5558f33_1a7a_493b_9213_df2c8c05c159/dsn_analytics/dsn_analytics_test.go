package dsn_analytics

import (
	"reflect"
	"testing"
)

// Node represents a DSN node with its users and directed connections.
type Node struct {
	Users       []string
	Connections []int
}

// TestAnalyzeDSN contains unit tests for the AnalyzeDSN function.
func TestAnalyzeDSN(t *testing.T) {
	tests := []struct {
		name          string
		N             int
		nodes         map[int]Node
		targetUserIDs []string
		expected      [][]int
	}{
		{
			name: "simple_path_found",
			N:    3,
			nodes: map[int]Node{
				0: {Users: []string{"userA", "userB"}, Connections: []int{1}},
				1: {Users: []string{"userC"}, Connections: []int{2}},
				2: {Users: []string{"userD"}, Connections: []int{}},
			},
			targetUserIDs: []string{"userA", "userD"},
			expected:      [][]int{{0, 1, 2}},
		},
		{
			name: "path_not_found_due_to_direction",
			N:    3,
			nodes: map[int]Node{
				0: {Users: []string{"userA", "userB"}, Connections: []int{1}},
				1: {Users: []string{"userC"}, Connections: []int{2}},
				2: {Users: []string{"userD"}, Connections: []int{}},
			},
			targetUserIDs: []string{"userD", "userA"},
			expected:      [][]int{{}},
		},
		{
			name: "target_users_on_same_node",
			N:    1,
			nodes: map[int]Node{
				0: {Users: []string{"userX", "userY"}, Connections: []int{}},
			},
			targetUserIDs: []string{"userX", "userY"},
			// Since both users are on node 0, the shortest path is [0]
			expected: [][]int{{0}},
		},
		{
			name: "multiple_targets_with_common_path",
			N:    4,
			nodes: map[int]Node{
				0: {Users: []string{"Alice"}, Connections: []int{1, 2}},
				1: {Users: []string{"Bob"}, Connections: []int{3}},
				2: {Users: []string{"Charlie"}, Connections: []int{3}},
				3: {Users: []string{"Daisy", "Eve"}, Connections: []int{}},
			},
			targetUserIDs: []string{"Alice", "Daisy", "Eve"},
			// Ordered pairs: 
			// Alice -> Daisy: expected path is [0,1,3] (BFS will choose 1 over 2)
			// Alice -> Eve: expected path is [0,1,3]
			// Daisy -> Eve: both on node 3, so expected path is [3]
			expected: [][]int{{0, 1, 3}, {0, 1, 3}, {3}},
		},
		{
			name: "nonexistent_user",
			N:    3,
			nodes: map[int]Node{
				0: {Users: []string{"userA", "userB"}, Connections: []int{1}},
				1: {Users: []string{"userC"}, Connections: []int{2}},
				2: {Users: []string{"userD"}, Connections: []int{}},
			},
			targetUserIDs: []string{"userX", "userA"},
			// Since userX does not exist, the path should be empty.
			expected: [][]int{{}},
		},
	}

	for _, tt := range tests {
		// Create a closure for queryNode that simulates retrieving node data.
		queryNode := func(nodeID int) ([]string, []int) {
			if node, ok := tt.nodes[nodeID]; ok {
				return node.Users, node.Connections
			}
			return []string{}, []int{}
		}

		result := AnalyzeDSN(tt.N, queryNode, tt.targetUserIDs)
		if !reflect.DeepEqual(result, tt.expected) {
			t.Errorf("Test %q failed:\nGot:  %v\nWant: %v", tt.name, result, tt.expected)
		}
	}
}

// BenchmarkAnalyzeDSN benchmarks the AnalyzeDSN function using a sample DSN.
func BenchmarkAnalyzeDSN(b *testing.B) {
	// Create a sample DSN with a moderate number of nodes.
	nodes := map[int]Node{
		0: {Users: []string{"userA"}, Connections: []int{1, 2}},
		1: {Users: []string{"userB"}, Connections: []int{3}},
		2: {Users: []string{"userC"}, Connections: []int{3}},
		3: {Users: []string{"userD"}, Connections: []int{4}},
		4: {Users: []string{"userE"}, Connections: []int{}},
	}
	N := 5
	targets := []string{"userA", "userE"}

	queryNode := func(nodeID int) ([]string, []int) {
		if node, ok := nodes[nodeID]; ok {
			return node.Users, node.Connections
		}
		return []string{}, []int{}
	}

	for i := 0; i < b.N; i++ {
		_ = AnalyzeDSN(N, queryNode, targets)
	}
}