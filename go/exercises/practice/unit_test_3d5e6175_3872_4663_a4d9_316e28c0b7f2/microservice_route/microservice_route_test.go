package microservice_route

import (
	"testing"
)

func TestMinCommunicationTime(t *testing.T) {
	type testCase struct {
		description  string
		N            int
		latency      [][]int
		K            int
		source       int
		destination  int
		expectedTime int
	}

	testCases := []testCase{
		{
			description:  "Direct connection available (simple 2-node)",
			N:            2,
			latency:      [][]int{{0, 10}, {-1, 0}},
			K:            5,
			source:       0,
			destination:  1,
			expectedTime: 10,
		},
		{
			description: "Route through one intermediate (no direct link)",
			N:           3,
			latency: [][]int{
				{0, 20, -1},
				{-1, 0, 20},
				{-1, -1, 0},
			},
			K:            5,
			source:       0,
			destination:  2,
			expectedTime: 45, // 20 (0->1) + 5 (overhead for 1) + 20 (1->2)
		},
		{
			description: "Better to use intermediate even when direct connection exists",
			N:           3,
			latency: [][]int{
				{0, 50, 100},
				{-1, 0, 10},
				{-1, -1, 0},
			},
			K:            5,
			source:       0,
			destination:  2,
			expectedTime: 65, // 50 (0->1) + 5 (overhead for 1) + 10 (1->2)
		},
		{
			description: "Ring network with cycle possibility",
			N:           4,
			latency: [][]int{
				{0, 5, -1, -1},
				{-1, 0, 5, -1},
				{-1, -1, 0, 5},
				{5, -1, -1, 0},
			},
			K:            2,
			source:       0,
			destination:  3,
			expectedTime: 19, // 0->1:5, overhead at 1:2, 1->2:5, overhead at 2:2, 2->3:5 => total 5+2+5+2+5 = 19
		},
		{
			description: "No available route",
			N:           3,
			latency: [][]int{
				{0, -1, -1},
				{-1, 0, -1},
				{-1, -1, 0},
			},
			K:            5,
			source:       0,
			destination:  2,
			expectedTime: -1,
		},
		{
			description: "Multiple routes available, choose optimal",
			N:           4,
			latency: [][]int{
				{0, 10, 50, 100},
				{10, 0, 10, -1},
				{50, 10, 0, 10},
				{100, -1, 10, 0},
			},
			K:            5,
			source:       0,
			destination:  3,
			expectedTime: 40, // best is 0->1->2->3: 10 + 10 + 10 + overhead 5*2 = 10+10+10+10 = 40
		},
		{
			description: "Self route (source equals destination)",
			N:           3,
			latency: [][]int{
				{0, 15, 30},
				{15, 0, 15},
				{30, 15, 0},
			},
			K:            5,
			source:       1,
			destination:  1,
			expectedTime: 0, // no travel required
		},
		{
			description: "Longer path with multiple intermediates",
			N:           5,
			latency: [][]int{
				{0,  10, -1, -1,  100},
				{-1,  0,  10, -1,  -1},
				{-1, -1,   0,  10, -1},
				{-1, -1,  -1,   0,  10},
				{-1, -1,  -1,  -1,   0},
			},
			K:            3,
			source:       0,
			destination:  4,
			expectedTime: 10 + 3 + 10 + 3 + 10 + 3 + 10, // 0->1->2->3->4: 10+10+10+10 + 3*3=40+9 = 49
		},
	}

	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			result := MinCommunicationTime(tc.N, tc.latency, tc.K, tc.source, tc.destination)
			if result != tc.expectedTime {
				t.Fatalf("for %s, expected %d but got %d", tc.description, tc.expectedTime, result)
			}
		})
	}
}