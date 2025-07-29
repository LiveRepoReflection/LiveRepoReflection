package city_traffic

import "testing"

// The function MinTravelTime is assumed to be implemented in the package with the following signature:
// func MinTravelTime(n int, roads [][]int, lightCost int, start int, end int, maxLights int) int

func TestMinTravelTime(t *testing.T) {
	testCases := []struct {
		description string
		n           int
		roads       [][]int
		lightCost   int
		start       int
		end         int
		maxLights   int
		expected    int
	}{
		{
			description: "Direct road with no intermediate intersections",
			n:           2,
			roads:       [][]int{{0, 1, 10}},
			lightCost:   5,
			start:       0,
			end:         1,
			maxLights:   0,
			expected:    10,
		},
		{
			description: "Two routes: one via an intermediate node without light installation",
			n:           3,
			roads:       [][]int{{0, 1, 10}, {1, 2, 10}, {0, 2, 25}},
			lightCost:   5,
			start:       0,
			end:         2,
			maxLights:   1,
			// Best route is 0->1->2 without installing a traffic light since start and end cannot be equipped.
			expected: 20,
		},
		{
			description: "Chain route with high-cost edge where direct route is optimal",
			n:           4,
			roads:       [][]int{{0, 1, 50}, {1, 2, 50}, {2, 3, 50}, {0, 3, 120}},
			lightCost:   10,
			start:       0,
			end:         3,
			maxLights:   2,
			// Even if installing lights on nodes 1 and 2 gives a discount on the middle edge,
			// the overall cost becomes: 50 (0->1) + 10 (wait at 1) + 25 (discounted 1->2) + 10 (wait at 2) + 50 (2->3) = 145.
			// The direct road cost is 120, which is lower.
			expected: 120,
		},
		{
			description: "Long chain where discount yields benefit on expensive roads",
			n:           5,
			roads:       [][]int{{0, 1, 100}, {1, 2, 100}, {2, 3, 100}, {3, 4, 100}, {0, 4, 500}},
			lightCost:   20,
			start:       0,
			end:         4,
			maxLights:   2,
			// Best route is 0->1->2->3->4 with optimal installation of lights on two of the three intermediate nodes.
			// For example, installing on nodes 1 and 2 yields:
			// 0->1: 100
			// wait at 1: 20
			// 1->2: discounted to 100/2 = 50 (both equipped)
			// wait at 2: 20
			// 2->3: no discount because 3 is not equipped = 100
			// 3->4: 100
			// Total = 100 + 20 + 50 + 20 + 100 + 100 = 390.
			expected: 390,
		},
		{
			description: "Graph with multiple potential routes; best is the direct low-cost chain",
			n:           6,
			roads: [][]int{
				{0, 1, 10},
				{1, 2, 10},
				{2, 5, 10},
				{0, 3, 20},
				{3, 4, 20},
				{4, 5, 20},
				{1, 4, 50},
				{2, 3, 50},
			},
			lightCost: 5,
			start:     0,
			end:       5,
			maxLights: 1,
			// Best route is 0->1->2->5 with cost 10+10+10 = 30.
			expected: 30,
		},
		{
			description: "Complex graph where installation does not improve the direct route",
			n:           5,
			roads: [][]int{
				{0, 1, 80},
				{1, 2, 80},
				{2, 4, 80},
				{0, 3, 100},
				{3, 2, 100},
				{1, 3, 30},
				{3, 4, 30},
			},
			lightCost: 10,
			start:     0,
			end:       4,
			maxLights: 1,
			// Evaluating routes:
			// Route 0->1->2->4: 80+80+80 = 240. Installing a light on either 1 or 2 does not yield discount on both sides.
			// Route 0->1->3->4: 80+30+30 = 140. Installing a light increases cost due to waiting time.
			// Route 0->3->4: 100+30 = 130. This is the best route.
			expected: 130,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := MinTravelTime(tc.n, tc.roads, tc.lightCost, tc.start, tc.end, tc.maxLights)
			if result != tc.expected {
				t.Fatalf("For test case '%s': expected %d, got %d", tc.description, tc.expected, result)
			}
		})
	}
}

func BenchmarkMinTravelTime(b *testing.B) {
	// Use a moderately sized test case for the benchmark.
	n := 50
	// Create a dense graph for benchmarking.
	var roads [][]int
	for i := 0; i < n; i++ {
		for j := i + 1; j < n; j++ {
			// Set road cost as a function of node indices to vary costs.
			cost := (i+j)%100 + 1
			roads = append(roads, []int{i, j, cost})
		}
	}
	lightCost := 10
	start := 0
	end := n - 1
	maxLights := n / 4

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = MinTravelTime(n, roads, lightCost, start, end, maxLights)
	}
}