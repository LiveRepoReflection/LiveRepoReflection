package task_schedule

import (
	"testing"
)

func TestTaskSchedule(t *testing.T) {
	tests := []struct {
		name     string
		n        int
		tasks    []Task
		expected int
	}{
		{
			name: "simple case with no dependencies",
			n:    2,
			tasks: []Task{
				{1, 5, 10, []int{}},
				{2, 3, 15, []int{}},
			},
			expected: 0,
		},
		{
			name: "tasks with dependencies",
			n:    3,
			tasks: []Task{
				{1, 5, 10, []int{}},
				{2, 3, 15, []int{1}},
				{3, 7, 20, []int{1, 2}},
			},
			expected: 0,
		},
		{
			name: "unavoidable penalty case",
			n:    3,
			tasks: []Task{
				{1, 5, 4, []int{}},  // Will miss deadline by 1
				{2, 3, 10, []int{1}}, // Will complete at 8 (deadline 10)
				{3, 4, 15, []int{2}}, // Will complete at 12 (deadline 15)
			},
			expected: 1,
		},
		{
			name: "complex dependencies",
			n:    5,
			tasks: []Task{
				{1, 2, 5, []int{}},
				{2, 3, 10, []int{1}},
				{3, 1, 15, []int{2}},
				{4, 4, 20, []int{1, 3}},
				{5, 2, 25, []int{4}},
			},
			expected: 0,
		},
		{
			name: "invalid dependencies should be ignored",
			n:    3,
			tasks: []Task{
				{1, 5, 10, []int{99}}, // Invalid dependency
				{2, 3, 15, []int{1}},
				{3, 7, 20, []int{1, 2}},
			},
			expected: 0,
		},
		{
			name: "single task with tight deadline",
			n:    1,
			tasks: []Task{
				{1, 5, 4, []int{}}, // Will miss deadline by 1
			},
			expected: 1,
		},
		{
			name: "parallel execution possible",
			n:    4,
			tasks: []Task{
				{1, 5, 10, []int{}},
				{2, 3, 10, []int{}},
				{3, 4, 15, []int{1}},
				{4, 2, 15, []int{2}},
			},
			expected: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := MinPenaltySchedule(tt.n, tt.tasks)
			if got != tt.expected {
				t.Errorf("MinPenaltySchedule() = %v, want %v", got, tt.expected)
			}
		})
	}
}

func BenchmarkTaskSchedule(b *testing.B) {
	tasks := []Task{
		{1, 5, 10, []int{}},
		{2, 3, 15, []int{1}},
		{3, 7, 20, []int{1, 2}},
		{4, 2, 25, []int{3}},
		{5, 4, 30, []int{4}},
	}
	n := 5

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MinPenaltySchedule(n, tasks)
	}
}