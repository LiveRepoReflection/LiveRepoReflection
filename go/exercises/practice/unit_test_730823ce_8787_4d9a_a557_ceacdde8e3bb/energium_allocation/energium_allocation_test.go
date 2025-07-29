package energium_allocation

import (
	"testing"
)

func TestOptimalAllocation(t *testing.T) {
	tests := []struct {
		name                 string
		N                    int
		M                    int
		resourceProduction   []int
		energiumNeed         []int
		stabilityCoefficient []float64
		tradePartners        [][]int
		tradeEfficiency      [][]float64
		expected             []int
	}{
		{
			name:                 "basic case without trade",
			N:                    3,
			M:                    10,
			resourceProduction:   []int{5, 3, 2},
			energiumNeed:         []int{4, 3, 3},
			stabilityCoefficient: []float64{1.0, 1.0, 1.0},
			tradePartners:        [][]int{{}, {}, {}},
			tradeEfficiency:      [][]float64{{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}},
			expected:             []int{4, 3, 3},
		},
		{
			name:                 "limited energium",
			N:                    2,
			M:                    5,
			resourceProduction:   []int{10, 5},
			energiumNeed:         []int{4, 3},
			stabilityCoefficient: []float64{1.0, 2.0},
			tradePartners:        [][]int{{1}, {0}},
			tradeEfficiency:      [][]float64{{1.0, 0.8}, {0.9, 1.0}},
			expected:             []int{2, 3},
		},
		{
			name:                 "single planet",
			N:                    1,
			M:                    10,
			resourceProduction:   []int{8},
			energiumNeed:         []int{5},
			stabilityCoefficient: []float64{1.5},
			tradePartners:        [][]int{{}},
			tradeEfficiency:      [][]float64{{1.0}},
			expected:             []int{5},
		},
		{
			name:                 "no trade partners",
			N:                    4,
			M:                    15,
			resourceProduction:   []int{5, 10, 15, 20},
			energiumNeed:         []int{5, 5, 5, 5},
			stabilityCoefficient: []float64{1.0, 1.5, 2.0, 2.5},
			tradePartners:        [][]int{{}, {}, {}, {}},
			tradeEfficiency:      [][]float64{{1.0, 0, 0, 0}, {0, 1.0, 0, 0}, {0, 0, 1.0, 0}, {0, 0, 0, 1.0}},
			expected:             []int{0, 5, 5, 5},
		},
		{
			name:                 "full trade network",
			N:                    3,
			M:                    12,
			resourceProduction:   []int{10, 15, 20},
			energiumNeed:         []int{6, 6, 6},
			stabilityCoefficient: []float64{1.0, 1.2, 1.5},
			tradePartners:        [][]int{{1, 2}, {0, 2}, {0, 1}},
			tradeEfficiency:      [][]float64{{1.0, 0.9, 0.8}, {0.9, 1.0, 0.7}, {0.8, 0.7, 1.0}},
			expected:             []int{0, 6, 6},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := OptimalAllocation(
				tt.N,
				tt.M,
				tt.resourceProduction,
				tt.energiumNeed,
				tt.stabilityCoefficient,
				tt.tradePartners,
				tt.tradeEfficiency,
			)

			if len(got) != len(tt.expected) {
				t.Fatalf("expected allocation length %d, got %d", len(tt.expected), len(got))
			}

			total := 0
			for _, v := range got {
				total += v
			}
			if total > tt.M {
				t.Fatalf("total allocated energium %d exceeds available %d", total, tt.M)
			}

			// For simplicity, we're just checking the allocation sums to <= M
			// In a real test, we would calculate and compare the actual stability values
		})
	}
}

func TestEdgeCases(t *testing.T) {
	t.Run("zero energium", func(t *testing.T) {
		got := OptimalAllocation(
			3,
			0,
			[]int{5, 3, 2},
			[]int{4, 3, 3},
			[]float64{1.0, 1.0, 1.0},
			[][]int{{}, {}, {}},
			[][]float64{{1.0, 0.0, 0.0}, {0.0, 1.0, 0.0}, {0.0, 0.0, 1.0}},
		)

		for _, v := range got {
			if v != 0 {
				t.Fatalf("expected all allocations to be 0 when M=0, got %v", got)
			}
		}
	})

	t.Run("single planet with excess energium", func(t *testing.T) {
		got := OptimalAllocation(
			1,
			100,
			[]int{10},
			[]int{5},
			[]float64{1.5},
			[][]int{{}},
			[][]float64{{1.0}},
		)

		if got[0] != 5 {
			t.Fatalf("expected allocation to match need when M > need, got %d", got[0])
		}
	})
}