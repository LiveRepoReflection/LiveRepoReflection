package task_orchestrator

import (
	"reflect"
	"testing"
	"time"
)

func TestTaskOrchestrator(t *testing.T) {
	tests := []struct {
		name           string
		tasks          map[string][]string
		workers        []string
		maxRetries     int
		simulateFunc   func(string) bool
		expectedStatus map[string]string
		expectError    bool
	}{
		{
			name: "Simple linear dependency",
			tasks: map[string][]string{
				"task1": {},
				"task2": {"task1"},
				"task3": {"task2"},
			},
			workers:    []string{"worker1", "worker2"},
			maxRetries: 3,
			simulateFunc: func(taskID string) bool {
				return true // All tasks succeed
			},
			expectedStatus: map[string]string{
				"task1": "completed",
				"task2": "completed",
				"task3": "completed",
			},
			expectError: false,
		},
		{
			name: "Circular dependency",
			tasks: map[string][]string{
				"task1": {"task3"},
				"task2": {"task1"},
				"task3": {"task2"},
			},
			workers:    []string{"worker1"},
			maxRetries: 3,
			simulateFunc: func(taskID string) bool {
				return true
			},
			expectedStatus: nil,
			expectError:    true,
		},
		{
			name: "Task failure with retries",
			tasks: map[string][]string{
				"task1": {},
				"task2": {"task1"},
			},
			workers:    []string{"worker1"},
			maxRetries: 2,
			simulateFunc: func(taskID string) bool {
				return false // All tasks fail
			},
			expectedStatus: map[string]string{
				"task1": "failed",
				"task2": "pending",
			},
			expectError: true,
		},
		{
			name: "Complex DAG",
			tasks: map[string][]string{
				"task1": {},
				"task2": {},
				"task3": {"task1", "task2"},
				"task4": {"task2"},
				"task5": {"task3", "task4"},
			},
			workers:    []string{"worker1", "worker2", "worker3"},
			maxRetries: 3,
			simulateFunc: func(taskID string) bool {
				return true
			},
			expectedStatus: map[string]string{
				"task1": "completed",
				"task2": "completed",
				"task3": "completed",
				"task4": "completed",
				"task5": "completed",
			},
			expectError: false,
		},
		{
			name:  "Empty task list",
			tasks: map[string][]string{},
			workers: []string{
				"worker1",
			},
			maxRetries: 3,
			simulateFunc: func(taskID string) bool {
				return true
			},
			expectedStatus: map[string]string{},
			expectError:    false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			orchestrator := NewOrchestrator(tt.tasks, tt.workers, tt.maxRetries, tt.simulateFunc)
			status, err := orchestrator.Execute()

			if tt.expectError && err == nil {
				t.Error("expected error but got none")
			}
			if !tt.expectError && err != nil {
				t.Errorf("unexpected error: %v", err)
			}
			if !tt.expectError && !reflect.DeepEqual(status, tt.expectedStatus) {
				t.Errorf("expected status %v, got %v", tt.expectedStatus, status)
			}
		})
	}
}

func TestWorkerFailure(t *testing.T) {
	tasks := map[string][]string{
		"task1": {},
		"task2": {"task1"},
	}
	workers := []string{"worker1", "worker2"}
	maxRetries := 3

	failOnFirst := make(map[string]bool)
	simulateFunc := func(taskID string) bool {
		if !failOnFirst[taskID] {
			failOnFirst[taskID] = true
			return false // First attempt fails
		}
		return true // Subsequent attempts succeed
	}

	orchestrator := NewOrchestrator(tasks, workers, maxRetries, simulateFunc)
	status, err := orchestrator.Execute()

	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	expectedStatus := map[string]string{
		"task1": "completed",
		"task2": "completed",
	}

	if !reflect.DeepEqual(status, expectedStatus) {
		t.Errorf("expected status %v, got %v", expectedStatus, status)
	}
}

func TestConcurrentExecution(t *testing.T) {
	tasks := map[string][]string{
		"task1": {},
		"task2": {},
		"task3": {"task1", "task2"},
	}
	workers := []string{"worker1", "worker2"}
	maxRetries := 3

	executionTimes := make(map[string]time.Time)
	simulateFunc := func(taskID string) bool {
		executionTimes[taskID] = time.Now()
		time.Sleep(100 * time.Millisecond)
		return true
	}

	orchestrator := NewOrchestrator(tasks, workers, maxRetries, simulateFunc)
	_, err := orchestrator.Execute()

	if err != nil {
		t.Errorf("unexpected error: %v", err)
	}

	// Check if task1 and task2 were executed concurrently
	timeDiff := executionTimes["task2"].Sub(executionTimes["task1"])
	if timeDiff > 50*time.Millisecond {
		t.Error("tasks were not executed concurrently")
	}

	// Check if task3 was executed after both task1 and task2
	if executionTimes["task3"].Before(executionTimes["task1"]) ||
		executionTimes["task3"].Before(executionTimes["task2"]) {
		t.Error("dependency order violated")
	}
}

func TestTaskCancellation(t *testing.T) {
	tasks := map[string][]string{
		"task1": {},
		"task2": {"task1"},
	}
	workers := []string{"worker1"}
	maxRetries := 3

	orchestrator := NewOrchestrator(tasks, workers, maxRetries, func(taskID string) bool {
		time.Sleep(100 * time.Millisecond)
		return true
	})

	go func() {
		time.Sleep(50 * time.Millisecond)
		orchestrator.Cancel()
	}()

	_, err := orchestrator.Execute()
	if err == nil {
		t.Error("expected cancellation error but got none")
	}
}

func BenchmarkOrchestrator(b *testing.B) {
	tasks := map[string][]string{
		"task1": {},
		"task2": {},
		"task3": {"task1", "task2"},
		"task4": {"task2"},
		"task5": {"task3", "task4"},
	}
	workers := []string{"worker1", "worker2", "worker3"}
	maxRetries := 3

	simulateFunc := func(taskID string) bool {
		return true
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		orchestrator := NewOrchestrator(tasks, workers, maxRetries, simulateFunc)
		orchestrator.Execute()
	}
}