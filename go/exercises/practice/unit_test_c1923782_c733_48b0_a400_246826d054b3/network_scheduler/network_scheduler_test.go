package network_scheduler

import (
	"testing"
)

// ScheduleTasks is assumed to be implemented in the network_scheduler package.
// It takes the number of nodes (N), number of tasks (M), a slice of node capacities (C),
// a slice of task processing requirements (P), and a slice of task deadlines (D).
// It returns a slice of integers representing the node assignment (1-indexed) for each task.
// If no valid schedule exists, it returns an empty slice.

// validAssignment checks whether the returned slice has length equal to M and
// that each task is assigned to a node in the range [1, N].
func validAssignment(assignments []int, N int, M int) bool {
	if len(assignments) != M {
		return false
	}
	for _, a := range assignments {
		if a < 1 || a > N {
			return false
		}
	}
	return true
}

func TestScheduleTasks_ValidCase(t *testing.T) {
	// Test case from the example:
	N := 2
	M := 3
	C := []int{6, 8}
	P := []int{3, 4, 2}
	D := []int{7, 8, 6}

	assignments := ScheduleTasks(N, M, C, P, D)

	if len(assignments) == 0 {
		t.Fatalf("Expected a valid schedule assignment, but got an empty slice")
	}
	if !validAssignment(assignments, N, M) {
		t.Fatalf("Assignment contains invalid node indices: %v", assignments)
	}
}

func TestScheduleTasks_ImpossibleCase(t *testing.T) {
	// Create an impossible scheduling scenario: a task's processing requirement exceeds its allowed deadline.
	N := 1
	M := 1
	C := []int{10}
	P := []int{10}
	D := []int{5} // Deadline is less than the processing requirement.

	assignments := ScheduleTasks(N, M, C, P, D)
	if len(assignments) != 0 {
		t.Fatalf("Expected scheduling to be impossible and return an empty slice, got: %v", assignments)
	}
}

func TestScheduleTasks_MultipleCases(t *testing.T) {
	testCases := []struct {
		name        string
		N           int
		M           int
		C           []int
		P           []int
		D           []int
		expectEmpty bool
	}{
		{
			name:        "Single node sequential scheduling",
			N:           1,
			M:           4,
			C:           []int{15},
			P:           []int{3, 5, 2, 4},
			D:           []int{10, 12, 8, 15},
			expectEmpty: false,
		},
		{
			name:        "Distribute tasks among nodes",
			N:           3,
			M:           5,
			C:           []int{5, 10, 7},
			P:           []int{4, 6, 3, 5, 2},
			D:           []int{8, 15, 6, 10, 7},
			expectEmpty: false,
		},
		{
			name:        "Tight deadlines making scheduling impossible",
			N:           2,
			M:           2,
			C:           []int{10, 10},
			P:           []int{5, 5},
			D:           []int{4, 4}, // Deadlines are too early for the tasks
			expectEmpty: true,
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			assignments := ScheduleTasks(tc.N, tc.M, tc.C, tc.P, tc.D)
			if tc.expectEmpty {
				if len(assignments) != 0 {
					t.Fatalf("Expected an empty assignment for impossible scheduling, got: %v", assignments)
				}
			} else {
				if len(assignments) == 0 {
					t.Fatalf("Expected a valid scheduling assignment, but got empty result for case: %s", tc.name)
				}
				if !validAssignment(assignments, tc.N, tc.M) {
					t.Fatalf("Assignment contains invalid node indices: %v", assignments)
				}
			}
		})
	}
}

func BenchmarkScheduleTasks(b *testing.B) {
	// Create a moderately complex scheduling scenario for benchmarking.
	N := 5
	M := 20
	C := []int{10, 12, 15, 10, 8}
	P := []int{3, 4, 5, 2, 6, 3, 4, 4, 5, 2, 3, 6, 4, 2, 5, 3, 4, 2, 7, 3}
	D := []int{10, 12, 15, 8, 14, 10, 11, 9, 15, 12, 10, 16, 13, 9, 12, 10, 11, 8, 17, 10}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		assignments := ScheduleTasks(N, M, C, P, D)
		if len(assignments) != 0 && !validAssignment(assignments, N, M) {
			b.Fatalf("Invalid assignment: %v", assignments)
		}
	}
}