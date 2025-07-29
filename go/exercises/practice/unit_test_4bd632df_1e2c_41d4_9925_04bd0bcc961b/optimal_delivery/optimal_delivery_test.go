package optimal_delivery

import (
	"math"
	"testing"
)

func TestCalculateMinMaxLatency(t *testing.T) {
	tests := []struct {
		name                 string
		N                    int
		adjMatrix            [][]int
		dataGenerationRates  []int
		processingCapacity   int
		expectedMinMaxLatency float64
	}{
		{
			name: "single node (just sink)",
			N:    1,
			adjMatrix: [][]int{
				{0},
			},
			dataGenerationRates:  []int{0},
			processingCapacity:   10,
			expectedMinMaxLatency: 0,
		},
		{
			name: "two nodes with direct connection",
			N:    2,
			adjMatrix: [][]int{
				{0, 5},
				{5, 0},
			},
			dataGenerationRates:  []int{0, 2},
			processingCapacity:   5,
			expectedMinMaxLatency: 5,
		},
		{
			name: "three nodes in line",
			N:    3,
			adjMatrix: [][]int{
				{0, 3, 0},
				{3, 0, 4},
				{0, 4, 0},
			},
			dataGenerationRates:  []int{0, 1, 2},
			processingCapacity:   3,
			expectedMinMaxLatency: 7,
		},
		{
			name: "star topology",
			N:    4,
			adjMatrix: [][]int{
				{0, 2, 2, 2},
				{2, 0, 0, 0},
				{2, 0, 0, 0},
				{2, 0, 0, 0},
			},
			dataGenerationRates:  []int{0, 1, 1, 1},
			processingCapacity:   2,
			expectedMinMaxLatency: 2,
		},
		{
			name: "overloaded node",
			N:    3,
			adjMatrix: [][]int{
				{0, 1, 0},
				{1, 0, 1},
				{0, 1, 0},
			},
			dataGenerationRates:  []int{0, 1, 10},
			processingCapacity:   5,
			expectedMinMaxLatency: math.MaxFloat64,
		},
		{
			name: "complex network with multiple paths",
			N:    5,
			adjMatrix: [][]int{
				{0, 2, 3, 0, 0},
				{2, 0, 1, 4, 0},
				{3, 1, 0, 2, 3},
				{0, 4, 2, 0, 1},
				{0, 0, 3, 1, 0},
			},
			dataGenerationRates:  []int{0, 2, 1, 3, 2},
			processingCapacity:   4,
			expectedMinMaxLatency: 6,
		},
		{
			name: "no data generation",
			N:    4,
			adjMatrix: [][]int{
				{0, 5, 0, 0},
				{5, 0, 3, 0},
				{0, 3, 0, 2},
				{0, 0, 2, 0},
			},
			dataGenerationRates:  []int{0, 0, 0, 0},
			processingCapacity:   1,
			expectedMinMaxLatency: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			actual := CalculateMinMaxLatency(tt.N, tt.adjMatrix, tt.dataGenerationRates, tt.processingCapacity)
			if tt.expectedMinMaxLatency == math.MaxFloat64 {
				if actual != math.MaxFloat64 {
					t.Errorf("expected infinite latency, got %f", actual)
				}
			} else if math.Abs(actual-tt.expectedMinMaxLatency) > 0.001 {
				t.Errorf("expected %f, got %f", tt.expectedMinMaxLatency, actual)
			}
		})
	}
}

func BenchmarkCalculateMinMaxLatency(b *testing.B) {
	N := 20
	adjMatrix := make([][]int, N)
	for i := range adjMatrix {
		adjMatrix[i] = make([]int, N)
		for j := range adjMatrix[i] {
			if i != j && (i+j)%3 == 0 {
				adjMatrix[i][j] = (i + j) % 10 + 1
			}
		}
	}
	dataGenerationRates := make([]int, N)
	for i := range dataGenerationRates {
		dataGenerationRates[i] = i % 3
	}
	processingCapacity := 5

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		CalculateMinMaxLatency(N, adjMatrix, dataGenerationRates, processingCapacity)
	}
}