package net_deploy

import (
	"math"
	"testing"
)

func floatEquals(a, b, tolerance float64) bool {
	return math.Abs(a-b) <= tolerance
}

type testCase struct {
	name           string
	capacities     []int
	links          [][]int
	latencies      []int
	deploymentCost int
	expected       float64
}

func TestOptimalDeployment(t *testing.T) {
	testCases := []testCase{
		{
			name:           "single node",
			capacities:     []int{100},
			links:          [][]int{},
			latencies:      []int{},
			deploymentCost: 50,
			// Only possible subset is either {} with 0 or {0} with 100-50 = 50. Maximum is 50.
			expected: 50,
		},
		{
			name:           "three nodes example",
			capacities:     []int{100, 150, 200},
			links:          [][]int{{0, 1}, {1, 2}},
			latencies:      []int{10, 20},
			deploymentCost: 50,
			// Possible subsets computation:
			// {}: 0
			// {0}: 100-50 = 50
			// {1}: 150-50 = 100
			// {2}: 200-50 = 150
			// {0,1}: capacity=250, connectivity: for 0: 1/10, for 1: 1/10, total=0.2, cost=100 => 250+0.2-100 = 150.2
			// {0,2}: not connected => 300-100 = 200
			// {1,2}: capacity=350, connectivity: for 1: 1/20, for 2: 1/20, total=0.1, cost=100 => 350+0.1-100 = 250.1
			// {0,1,2}: capacity=450, connectivity: 
			//    node0: neighbor 1 => 1/10 = 0.1
			//    node1: neighbors 0 (1/10) and 2 (1/20) => 0.1 + 0.05 = 0.15
			//    node2: neighbor 1 => 1/20 = 0.05
			// Total connectivity = 0.1+0.15+0.05 = 0.3, cost=150, utility=450+0.3-150 = 300.3
			// Maximum utility = 300.3
			expected: 300.3,
		},
		{
			name:           "disconnected centers with one link",
			capacities:     []int{100, 200, 300, 400},
			links:          [][]int{{1, 2}},
			latencies:      []int{50},
			deploymentCost: 100,
			// Evaluate some subsets:
			// {}: 0
			// Single nodes: best is node3 with 400-100 = 300.
			// {1,2}: capacity=500, connectivity: for 1: 1/50, for 2: 1/50, sum=0.04, cost=200 => 500+0.04-200 = 300.04
			// All nodes: capacity=1000, connectivity: only link exists between 1 and 2 giving both bonus = 1/50 each = 0.04, cost=400 => 1000+0.04-400 = 600.04
			// Maximum utility = 600.04
			expected: 600.04,
		},
		{
			name:           "negative outcomes, best empty",
			capacities:     []int{10, 10},
			links:          [][]int{{0, 1}},
			latencies:      []int{1},
			deploymentCost: 20,
			// Subset {}: 0
			// {0}: 10-20 = -10
			// {1}: 10-20 = -10
			// {0,1}: capacity=20, connectivity: node0 gets 1, node1 gets 1 (if both counted) total = 2, cost=40: 20+2-40 = -18
			// Maximum is 0 (empty subset)
			expected: 0,
		},
		{
			name:           "triangle network",
			capacities:     []int{100, 100, 100},
			links:          [][]int{{0, 1}, {1, 2}, {0, 2}},
			latencies:      []int{5, 10, 20},
			deploymentCost: 50,
			// Evaluate:
			// {0,1}: capacity=200, connectivity: node0: 1/5, node1: 1/5, total=0.4, cost=100 => 200+0.4-100 = 100.4
			// {0,2}: capacity=200, connectivity: node0: 1/20, node2: 1/20, total=0.1, utility=200+0.1-100 = 100.1
			// {1,2}: capacity=200, connectivity: node1: 1/10, node2: 1/10, total=0.2, utility=200+0.2-100 = 100.2
			// {0,1,2}: capacity=300, connectivity:
			//   node0: neighbors: 1 (1/5=0.2), 2 (1/20=0.05) => 0.25
			//   node1: neighbors: 0 (0.2), 2 (1/10=0.1) => 0.3
			//   node2: neighbors: 0 (0.05), 1 (0.1) => 0.15
			// Total connectivity = 0.25+0.3+0.15 = 0.7, cost=150, utility = 300+0.7-150 = 150.7
			// Maximum = 150.7
			expected: 150.7,
		},
	}

	tolerance := 1e-6

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			result := OptimalDeployment(tc.capacities, tc.links, tc.latencies, tc.deploymentCost)
			if !floatEquals(result, tc.expected, tolerance) {
				t.Errorf("Test case %q failed: expected %f, got %f", tc.name, tc.expected, result)
			}
		})
	}
}