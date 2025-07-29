package quantum_network

import (
	"testing"
)

func TestMinEntangledLinks(t *testing.T) {
	tests := []struct {
		name               string
		n                  int
		entanglementMatrix [][]bool
		coherenceLevels    []int
		source             int
		destination        int
		want               int
	}{
		{
			name: "direct connection",
			n:    2,
			entanglementMatrix: [][]bool{
				{false, true},
				{true, false},
			},
			coherenceLevels: []int{90, 80},
			source:          0,
			destination:     1,
			want:            1,
		},
		{
			name: "no connection",
			n:    3,
			entanglementMatrix: [][]bool{
				{false, true, false},
				{true, false, false},
				{false, false, false},
			},
			coherenceLevels: []int{80, 70, 90},
			source:          0,
			destination:     2,
			want:            -1,
		},
		{
			name: "multiple paths with coherence preference",
			n:    5,
			entanglementMatrix: [][]bool{
				{false, true, true, false, false},
				{true, false, true, false, true},
				{true, true, false, true, false},
				{false, false, true, false, true},
				{false, true, false, true, false},
			},
			coherenceLevels: []int{80, 90, 70, 60, 50},
			source:          0,
			destination:     4,
			want:            2,
		},
		{
			name: "same node",
			n:    1,
			entanglementMatrix: [][]bool{
				{false},
			},
			coherenceLevels: []int{100},
			source:          0,
			destination:     0,
			want:            0,
		},
		{
			name: "large network with optimal path",
			n:    6,
			entanglementMatrix: [][]bool{
				{false, true, false, false, false, false},
				{true, false, true, true, false, false},
				{false, true, false, false, true, false},
				{false, true, false, false, true, true},
				{false, false, true, true, false, true},
				{false, false, false, true, true, false},
			},
			coherenceLevels: []int{80, 85, 75, 90, 70, 65},
			source:          0,
			destination:     5,
			want:            3,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := MinEntangledLinks(tt.n, tt.entanglementMatrix, tt.coherenceLevels, tt.source, tt.destination)
			if got != tt.want {
				t.Errorf("MinEntangledLinks() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkMinEntangledLinks(b *testing.B) {
	n := 500
	matrix := make([][]bool, n)
	for i := range matrix {
		matrix[i] = make([]bool, n)
		for j := range matrix[i] {
			if i != j && (i+j)%3 == 0 {
				matrix[i][j] = true
			}
		}
	}
	coherence := make([]int, n)
	for i := range coherence {
		coherence[i] = 50 + i%50
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MinEntangledLinks(n, matrix, coherence, 0, n-1)
	}
}