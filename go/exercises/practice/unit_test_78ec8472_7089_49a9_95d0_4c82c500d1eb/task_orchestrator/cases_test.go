package task_orchestrator

var testCases = []struct {
	description    string
	tasks          map[string][]string
	workers        []string
	maxRetries     int
	expectedStatus map[string]string
	expectError    bool
}{
	{
		description: "single task no dependencies",
		tasks: map[string][]string{
			"task1": {},
		},
		workers:    []string{"worker1"},
		maxRetries: 3,
		expectedStatus: map[string]string{
			"task1": "completed",
		},
		expectError: false,
	},
	{
		description: "two independent tasks",
		tasks: map[string][]string{
			"task1": {},
			"task2": {},
		},
		workers:    []string{"worker1", "worker2"},
		maxRetries: 3,
		expectedStatus: map[string]string{
			"task1": "completed",
			"task2": "completed",
		},
		expectError: false,
	},
	{
		description: "linear dependency chain",
		tasks: map[string][]string{
			"task1": {},
			"task2": {"task1"},
			"task3": {"task2"},
		},
		workers:    []string{"worker1"},
		maxRetries: 3,
		expectedStatus: map[string]string{
			"task1": "completed",
			"task2": "completed",
			"task3": "completed",
		},
		expectError: false,
	},
	{
		description: "complex dependency graph",
		tasks: map[string][]string{
			"task1": {},
			"task2": {},
			"task3": {"task1", "task2"},
			"task4": {"task2"},
			"task5": {"task3", "task4"},
		},
		workers:    []string{"worker1", "worker2", "worker3"},
		maxRetries: 3,
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
		description: "circular dependency",
		tasks: map[string][]string{
			"task1": {"task2"},
			"task2": {"task1"},
		},
		workers:    []string{"worker1"},
		maxRetries: 3,
		expectedStatus: nil,
		expectError:    true,
	},
}