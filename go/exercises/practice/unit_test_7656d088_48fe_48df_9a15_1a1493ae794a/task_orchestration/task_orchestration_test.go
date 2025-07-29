package task_orchestration

import (
	"reflect"
	"testing"
)

func validateAssignment(t *testing.T, n int, m int, capacities []int, requirements []int, assignment map[int][]int, failedNode int) {
	// Each task should be assigned exactly once.
	taskCount := make([]int, m)
	for node, tasks := range assignment {
		// Skip failed node: tasks should not be allocated there.
		if node == failedNode {
			if len(tasks) != 0 {
				t.Errorf("Failed node %d should have no tasks assigned, got %v", failedNode, tasks)
			}
		}
		totalRes := 0
		for _, taskIndex := range tasks {
			if taskIndex < 0 || taskIndex >= m {
				t.Errorf("Task index %d out of range", taskIndex)
			}
			taskCount[taskIndex]++
			totalRes += requirements[taskIndex]
		}
		if totalRes > capacities[node] {
			t.Errorf("Node %d capacity exceeded: required %d, capacity %d", node, totalRes, capacities[node])
		}
	}
	for i, count := range taskCount {
		if count != 1 {
			t.Errorf("Task %d is assigned %d times; expected exactly 1 assignment", i, count)
		}
	}
}

func TestOptimalAssignmentNoFailure(t *testing.T) {
	n := 3
	m := 5
	capacities := []int{10, 12, 8}
	requirements := []int{3, 4, 2, 5, 1}
	times := [][]int{
		{5, 7, 9},
		{8, 6, 4},
		{2, 3, 5},
		{6, 8, 7},
		{1, 2, 3},
	}
	failedNode := -1

	assignment, err := OptimalAssignment(n, m, capacities, requirements, times, failedNode)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if len(assignment) == 0 {
		t.Fatalf("Expected valid assignment, got empty map")
	}
	validateAssignment(t, n, m, capacities, requirements, assignment, failedNode)
}

func TestOptimalAssignmentWithFailure(t *testing.T) {
	n := 3
	m := 5
	capacities := []int{10, 12, 8}
	requirements := []int{3, 4, 2, 5, 1}
	times := [][]int{
		{5, 7, 9},
		{8, 6, 4},
		{2, 3, 5},
		{6, 8, 7},
		{1, 2, 3},
	}
	failedNode := 1

	assignment, err := OptimalAssignment(n, m, capacities, requirements, times, failedNode)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if tasks, exists := assignment[failedNode]; exists && len(tasks) != 0 {
		t.Fatalf("Failed node %d should have no tasks assigned, but got %v", failedNode, tasks)
	}
	validateAssignment(t, n, m, capacities, requirements, assignment, failedNode)
}

func TestInfeasibleAssignment(t *testing.T) {
	n := 2
	m := 3
	capacities := []int{5, 5}
	requirements := []int{4, 4, 4}
	times := [][]int{
		{3, 4},
		{2, 5},
		{6, 3},
	}
	failedNode := -1

	assignment, err := OptimalAssignment(n, m, capacities, requirements, times, failedNode)
	// Expect empty assignment due to infeasibility
	if err == nil && len(assignment) != 0 {
		t.Fatalf("Expected empty assignment due to infeasible resource allocation, got: %v", assignment)
	}
}

func TestAllNodesFail(t *testing.T) {
	n := 3
	m := 2
	capacities := []int{10, 10, 10}
	requirements := []int{3, 4}
	times := [][]int{
		{5, 5, 5},
		{6, 6, 6},
	}
	// Simulate failure scenario by reducing capacities of available nodes.
	failedNode := 0
	capacities[1] = 3
	capacities[2] = 3

	assignment, err := OptimalAssignment(n, m, capacities, requirements, times, failedNode)
	if err == nil && len(assignment) != 0 {
		t.Fatalf("Expected empty assignment due to infeasibility after node failure, got: %v", assignment)
	}
}

func TestEdgeCaseSingleTaskSingleNode(t *testing.T) {
	n := 1
	m := 1
	capacities := []int{10}
	requirements := []int{5}
	times := [][]int{
		{7},
	}
	failedNode := -1

	assignment, err := OptimalAssignment(n, m, capacities, requirements, times, failedNode)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	expected := map[int][]int{
		0: {0},
	}
	if !reflect.DeepEqual(assignment, expected) {
		t.Fatalf("Expected assignment %v, got %v", expected, assignment)
	}
	validateAssignment(t, n, m, capacities, requirements, assignment, failedNode)
}