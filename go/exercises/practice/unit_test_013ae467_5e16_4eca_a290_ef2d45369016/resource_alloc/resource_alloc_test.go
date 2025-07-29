package resource_alloc

import (
	"testing"
)

func TestOptimalResourceAllocation(t *testing.T) {
	tests := []struct {
		name               string
		N                  int
		M                  int
		serviceRequirements [][]int
		machineCapacities  [][]int
		costMatrix         [][]int
		instanceCount      []int
		want              int
	}{
		{
			name: "Basic feasible case",
			N:    2,
			M:    2,
			serviceRequirements: [][]int{
				{2, 3}, // Service 0 requires 2 CPU, 3 Memory
				{3, 2}, // Service 1 requires 3 CPU, 2 Memory
			},
			machineCapacities: [][]int{
				{3, 4}, // Machine 0 has 3 CPU, 4 Memory
				{4, 3}, // Machine 1 has 4 CPU, 3 Memory
			},
			costMatrix: [][]int{
				{1, 2}, // Cost of placing service 0 on machines
				{2, 1}, // Cost of placing service 1 on machines
			},
			instanceCount: []int{1, 1},
			want:         2, // Optimal allocation costs 2
		},
		{
			name: "Infeasible case - insufficient resources",
			N:    2,
			M:    2,
			serviceRequirements: [][]int{
				{5, 5},
				{5, 5},
			},
			machineCapacities: [][]int{
				{4, 4},
				{4, 4},
			},
			costMatrix: [][]int{
				{1, 1},
				{1, 1},
			},
			instanceCount: []int{1, 1},
			want:         -1,
		},
		{
			name: "Complex case with multiple resources",
			N:    3,
			M:    3,
			serviceRequirements: [][]int{
				{2, 3, 1}, // CPU, Memory, Network
				{1, 2, 3},
				{3, 1, 2},
			},
			machineCapacities: [][]int{
				{3, 4, 4},
				{4, 3, 4},
				{4, 4, 3},
			},
			costMatrix: [][]int{
				{1, 2, 3},
				{3, 1, 2},
				{2, 3, 1},
			},
			instanceCount: []int{1, 1, 1},
			want:         3,
		},
		{
			name: "Multiple instances",
			N:    2,
			M:    2,
			serviceRequirements: [][]int{
				{1, 1},
				{2, 2},
			},
			machineCapacities: [][]int{
				{4, 4},
				{4, 4},
			},
			costMatrix: [][]int{
				{1, 2},
				{2, 1},
			},
			instanceCount: []int{2, 1},
			want:         3,
		},
		{
			name: "Edge case - single machine",
			N:    2,
			M:    1,
			serviceRequirements: [][]int{
				{1, 1},
				{1, 1},
			},
			machineCapacities: [][]int{
				{3, 3},
			},
			costMatrix: [][]int{
				{1},
				{1},
			},
			instanceCount: []int{1, 1},
			want:         2,
		},
		{
			name: "Edge case - single service",
			N:    1,
			M:    2,
			serviceRequirements: [][]int{
				{1, 1},
			},
			machineCapacities: [][]int{
				{2, 2},
				{2, 2},
			},
			costMatrix: [][]int{
				{1, 2},
			},
			instanceCount: []int{1},
			want:         1,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := OptimalResourceAllocation(tt.N, tt.M, tt.serviceRequirements,
				tt.machineCapacities, tt.costMatrix, tt.instanceCount)
			if got != tt.want {
				t.Errorf("OptimalResourceAllocation() = %v, want %v", got, tt.want)
			}
		})
	}
}

// Benchmark to test performance
func BenchmarkOptimalResourceAllocation(b *testing.B) {
	N, M := 5, 5
	serviceRequirements := [][]int{
		{2, 3, 1},
		{1, 2, 3},
		{3, 1, 2},
		{2, 2, 2},
		{1, 3, 2},
	}
	machineCapacities := [][]int{
		{4, 4, 4},
		{4, 4, 4},
		{4, 4, 4},
		{4, 4, 4},
		{4, 4, 4},
	}
	costMatrix := [][]int{
		{1, 2, 3, 4, 5},
		{2, 1, 2, 3, 4},
		{3, 2, 1, 2, 3},
		{4, 3, 2, 1, 2},
		{5, 4, 3, 2, 1},
	}
	instanceCount := []int{1, 1, 1, 1, 1}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		OptimalResourceAllocation(N, M, serviceRequirements,
			machineCapacities, costMatrix, instanceCount)
	}
}