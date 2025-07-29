package billboard_placement

import "testing"

func TestMaxRevenue(t *testing.T) {
	type testCase struct {
		description string
		positions   []int
		revenue     []int
		minDistance int
		expected    int
	}

	cases := []testCase{
		{
			description: "example case 1",
			positions:   []int{1, 2, 3, 6},
			revenue:     []int{5, 1, 3, 5},
			minDistance: 2,
			expected:    10,
		},
		{
			description: "example case 2",
			positions:   []int{1, 4, 5, 8, 9},
			revenue:     []int{3, 5, 1, 4, 2},
			minDistance: 3,
			expected:    9,
		},
		{
			description: "single location",
			positions:   []int{10},
			revenue:     []int{100},
			minDistance: 5,
			expected:    100,
		},
		{
			description: "better chain selection",
			positions:   []int{1, 3, 6, 10, 15},
			revenue:     []int{5, 6, 5, 20, 20},
			minDistance: 4,
			// Best selection: positions 3, 10 and 15 => 6 + 20 + 20 = 46
			expected: 46,
		},
		{
			description: "duplicate positions",
			positions:   []int{1, 1, 10},
			revenue:     []int{10, 20, 30},
			minDistance: 1,
			// Only one billboard can be placed at position 1; best pick the one with revenue 20, then position 10 => 20 + 30 = 50
			expected: 50,
		},
		{
			description: "no pair allowed",
			positions:   []int{5, 10, 15},
			revenue:     []int{10, 15, 20},
			minDistance: 20,
			// Cannot pick any two together, so the best is the maximum single revenue.
			expected: 20,
		},
	}

	for _, tc := range cases {
		result := MaxRevenue(tc.positions, tc.revenue, tc.minDistance)
		if result != tc.expected {
			t.Errorf("Test %q failed: expected %d, got %d", tc.description, tc.expected, result)
		}
	}
}

func BenchmarkMaxRevenue(b *testing.B) {
	positions := []int{1, 2, 3, 6, 10, 15, 21, 28, 36, 45, 55, 66, 78, 91, 105}
	revenue := []int{5, 1, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987}
	minDistance := 5

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = MaxRevenue(positions, revenue, minDistance)
	}
}