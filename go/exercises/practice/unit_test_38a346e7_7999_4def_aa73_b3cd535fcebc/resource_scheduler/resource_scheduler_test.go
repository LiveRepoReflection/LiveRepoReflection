package resource_scheduler

import (
	"reflect"
	"testing"
)

// We assume that the function ScheduleTasks is implemented in the resource_scheduler package with the following signature:
// func ScheduleTasks(n int, m int, workers [][]int, tasks [][]int) int

func TestScheduleTasks(t *testing.T) {
	tests := []struct {
		description string
		n           int
		m           int
		workers     [][]int
		tasks       [][]int
		expected    int
	}{
		{
			description: "Basic scheduling with two workers and three tasks",
			n:           2,
			m:           3,
			workers: [][]int{
				{4, 4, 4},
				{3, 3, 3},
			},
			// Each task: [cpu, ram, disk, priority]
			tasks: [][]int{
				{2, 2, 2, 1},
				{1, 1, 1, 2},
				{3, 3, 3, 3},
			},
			expected: 3,
		},
		{
			description: "No tasks can be scheduled due to high requirements",
			n:           1,
			m:           2,
			workers: [][]int{
				{5, 5, 5},
			},
			tasks: [][]int{
				{6, 5, 5, 10},
				{5, 6, 5, 9},
			},
			expected: 0,
		},
		{
			description: "Exact resource matching on single worker",
			n:           1,
			m:           2,
			workers: [][]int{
				{5, 5, 5},
			},
			tasks: [][]int{
				{3, 3, 3, 5},
				{2, 2, 2, 10},
			},
			expected: 2,
		},
		{
			description: "Multiple tasks scheduled on one worker",
			n:           1,
			m:           5,
			workers: [][]int{
				{10, 10, 10},
			},
			tasks: [][]int{
				{2, 2, 2, 1},
				{3, 3, 3, 2},
				{1, 1, 1, 3},
				{2, 2, 2, 4},
				{2, 2, 2, 5},
			},
			expected: 5,
		},
		{
			description: "Tasks spread across two workers with limited resources",
			n:           2,
			m:           4,
			workers: [][]int{
				{5, 5, 5},
				{4, 4, 4},
			},
			tasks: [][]int{
				{3, 3, 3, 6},
				{2, 2, 2, 8},
				{3, 3, 3, 5},
				{1, 1, 1, 7},
			},
			// In an optimal schedule:
			// Worker 1: {2,2,2,8} then {3,3,3,5} may not both fit, but instead:
			// Worker 1: {2,2,2,8} and {1,1,1,7} (total: 3,3,3) leaving resources for no additional task.
			// Worker 2: {3,3,3,6} fits. Expected scheduled tasks = 3.
			expected: 3,
		},
		{
			description: "Multiple tasks with identical priorities",
			n:           2,
			m:           6,
			workers: [][]int{
				{7, 7, 7},
				{5, 5, 5},
			},
			tasks: [][]int{
				{3, 3, 3, 5},
				{3, 3, 3, 5},
				{2, 2, 2, 5},
				{2, 2, 2, 5},
				{4, 4, 4, 5},
				{1, 1, 1, 5},
			},
			// Expected scheduling may vary as tasks have same priority.
			// One optimal scheduling:
			// Worker 1: {4,4,4,5} + {2,2,2,5} + {1,1,1,5} = total resource usage = (7,7,7)
			// Worker 2: {3,3,3,5} fits, but the remaining tasks {3,3,3,5} or {2,2,2,5} cannot be scheduled.
			// Thus expected scheduled tasks = 4.
			expected: 4,
		},
	}

	for _, tc := range tests {
		t.Run(tc.description, func(t *testing.T) {
			result := ScheduleTasks(tc.n, tc.m, tc.workers, tc.tasks)
			if !reflect.DeepEqual(result, tc.expected) {
				t.Errorf("Test '%s' failed. Expected %d tasks to be scheduled, got %d", tc.description, tc.expected, result)
			}
		})
	}
}

func BenchmarkScheduleTasks(b *testing.B) {
	// Benchmark with moderately large inputs
	n := 100
	m := 100
	workers := make([][]int, n)
	for i := 0; i < n; i++ {
		workers[i] = []int{1000, 1000, 1000}
	}
	tasks := make([][]int, m)
	for j := 0; j < m; j++ {
		// Vary resource needs and random-ish priorities
		tasks[j] = []int{j % 10 + 1, j % 10 + 1, j % 10 + 1, (j % 50) + 1}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		ScheduleTasks(n, m, workers, tasks)
	}
}