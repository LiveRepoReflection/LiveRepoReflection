package task_assign

import (
	"testing"
)

func TestMinCostAssignment(t *testing.T) {
	tests := []struct {
		name            string
		N               int
		M               int
		engineerSkills  []int
		taskSkills      []int
		cost            [][]int
		expectedMinCost int
	}{
		{
			name:            "basic assignment possible",
			N:               3,
			M:               3,
			engineerSkills:  []int{7, 6, 3},
			taskSkills:      []int{1, 2, 4},
			cost:            [][]int{{1, 2, 3}, {4, 5, 6}, {7, 8, 9}},
			expectedMinCost: 15,
		},
		{
			name:            "impossible assignment due to skills",
			N:               2,
			M:               2,
			engineerSkills:  []int{1, 2},
			taskSkills:      []int{4, 8},
			cost:            [][]int{{1, 2}, {3, 4}},
			expectedMinCost: -1,
		},
		{
			name:            "single engineer multiple tasks",
			N:               1,
			M:               2,
			engineerSkills:  []int{3},
			taskSkills:      []int{1, 2},
			cost:            [][]int{{5, 10}},
			expectedMinCost: -1,
		},
		{
			name:            "multiple engineers single task",
			N:               3,
			M:               1,
			engineerSkills:  []int{1, 3, 7},
			taskSkills:      []int{1},
			cost:            [][]int{{5}, {3}, {1}},
			expectedMinCost: 1,
		},
		{
			name:            "large cost difference",
			N:               2,
			M:               2,
			engineerSkills:  []int{3, 7},
			taskSkills:      []int{1, 2},
			cost:            [][]int{{100, 1}, {1, 100}},
			expectedMinCost: 2,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			actual := MinCostAssignment(tt.N, tt.M, tt.engineerSkills, tt.taskSkills, tt.cost)
			if actual != tt.expectedMinCost {
				t.Errorf("MinCostAssignment() = %v, want %v", actual, tt.expectedMinCost)
			}
		})
	}
}

func BenchmarkMinCostAssignment(b *testing.B) {
	N := 10
	M := 10
	engineerSkills := make([]int, N)
	taskSkills := make([]int, M)
	cost := make([][]int, N)

	for i := 0; i < N; i++ {
		engineerSkills[i] = (1 << 16) - 1
		taskSkills[i] = 1 << i
		cost[i] = make([]int, M)
		for j := 0; j < M; j++ {
			cost[i][j] = (i + j) % 100
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MinCostAssignment(N, M, engineerSkills, taskSkills, cost)
	}
}