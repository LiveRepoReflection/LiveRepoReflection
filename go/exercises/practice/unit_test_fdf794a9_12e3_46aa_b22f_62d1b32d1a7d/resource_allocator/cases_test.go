package resource_allocator

// This is an auto-generated file. Do not change it manually.

var testNodes = []struct {
	id     string
	cpu    int
	memory int
	disk   int
}{
	{id: "node1", cpu: 8, memory: 16384, disk: 1000},
	{id: "node2", cpu: 16, memory: 32768, disk: 2000},
	{id: "node3", cpu: 4, memory: 8192, disk: 500},
	{id: "node4", cpu: 32, memory: 65536, disk: 4000},
}

var simpleAllocationTestCases = []struct {
	description        string
	jobs               []job
	expectedAllocation map[string]string
}{
	{
		description: "Simple allocation of a single job",
		jobs: []job{
			{id: "job1", priority: 1, cpu: 4, memory: 8192, disk: 500},
		},
		expectedAllocation: map[string]string{
			"job1": "node1",
		},
	},
	{
		description: "Allocation of multiple jobs",
		jobs: []job{
			{id: "job1", priority: 1, cpu: 4, memory: 8192, disk: 500},
			{id: "job2", priority: 1, cpu: 8, memory: 16384, disk: 1000},
			{id: "job3", priority: 1, cpu: 2, memory: 4096, disk: 200},
		},
		expectedAllocation: map[string]string{
			"job1": "node1",
			"job2": "node2",
			"job3": "node3",
		},
	},
	{
		description: "Allocation with insufficient resources",
		jobs: []job{
			{id: "job1", priority: 1, cpu: 4, memory: 8192, disk: 500},
			{id: "job2", priority: 1, cpu: 16, memory: 32768, disk: 2000},
			{id: "job3", priority: 1, cpu: 32, memory: 65536, disk: 4000},
			{id: "job4", priority: 1, cpu: 8, memory: 16384, disk: 1000}, // This should not be allocated
		},
		expectedAllocation: map[string]string{
			"job1": "node1",
			"job2": "node2",
			"job3": "node4",
		},
	},
}

var priorityAllocationTestCases = []struct {
	description        string
	jobs               []job
	expectedAllocation map[string]string
}{
	{
		description: "Higher priority job should be allocated first",
		jobs: []job{
			{id: "job1", priority: 1, cpu: 4, memory: 8192, disk: 500},
			{id: "job2", priority: 3, cpu: 4, memory: 8192, disk: 500},
			{id: "job3", priority: 2, cpu: 4, memory: 8192, disk: 500},
		},
		expectedAllocation: map[string]string{
			"job2": "node1",
			"job3": "node2",
			"job1": "node4",
		},
	},
	{
		description: "Higher priority job should preempt lower priority jobs if preemption is enabled",
		jobs: []job{
			{id: "job1", priority: 1, cpu: 8, memory: 16384, disk: 1000},
			{id: "job2", priority: 1, cpu: 16, memory: 32768, disk: 2000},
			{id: "job3", priority: 1, cpu: 4, memory: 8192, disk: 500},
			{id: "job4", priority: 3, cpu: 40, memory: 81920, disk: 5000}, // This requires preemption
		},
		expectedAllocation: map[string]string{
			"job1": "node1",
			"job2": "node2",
			"job3": "node3",
		},
	},
}

var affinityAllocationTestCases = []struct {
	description        string
	jobs               []job
	expectedAllocation map[string]string
}{
	{
		description: "Job with node affinity should be allocated to preferred node",
		jobs: []job{
			{id: "job1", priority: 1, cpu: 4, memory: 8192, disk: 500, preferredNodes: []string{"node3"}},
		},
		expectedAllocation: map[string]string{
			"job1": "node3",
		},
	},
	{
		description: "Job with node affinity should be allocated to alternative if preferred not available",
		jobs: []job{
			{id: "job1", priority: 1, cpu: 4, memory: 8192, disk: 500, preferredNodes: []string{"node5", "node6"}},
		},
		expectedAllocation: map[string]string{
			"job1": "node1", // or another available node
		},
	},
	{
		description: "Jobs with competing affinities",
		jobs: []job{
			{id: "job1", priority: 1, cpu: 2, memory: 4096, disk: 250, preferredNodes: []string{"node3"}},
			{id: "job2", priority: 2, cpu: 2, memory: 4096, disk: 250, preferredNodes: []string{"node3"}},
		},
		expectedAllocation: map[string]string{
			"job2": "node3", // Higher priority gets the preferred node
			"job1": "node1", // Lower priority gets another node
		},
	},
}

var complexAllocationTestCases = []struct {
	description        string
	jobs               []job
	expectedAllocation map[string]string
}{
	{
		description: "Complex scenario with priorities, affinities, and resource constraints",
		jobs: []job{
			{id: "job1", priority: 2, cpu: 4, memory: 8192, disk: 500, preferredNodes: []string{"node1"}},
			{id: "job2", priority: 3, cpu: 8, memory: 16384, disk: 1000, preferredNodes: []string{"node2"}},
			{id: "job3", priority: 1, cpu: 2, memory: 4096, disk: 200, preferredNodes: []string{"node3"}},
			{id: "job4", priority: 4, cpu: 16, memory: 32768, disk: 2000, preferredNodes: []string{"node4"}},
			{id: "job5", priority: 1, cpu: 4, memory: 8192, disk: 500},
		},
		expectedAllocation: map[string]string{
			"job4": "node4", // Highest priority gets preferred node
			"job2": "node2", // Next highest gets preferred node
			"job1": "node1", // Next gets preferred node
			"job3": "node3", // Lowest with preference gets preferred node
		},
	},
}

var releaseResourcesTestCases = []struct {
	description          string
	initialJobs          []job
	jobsToRelease        []string
	secondaryJobs        []job
	expectedInitialAlloc map[string]string
	expectedFinalAlloc   map[string]string
}{
	{
		description: "Release resources and allocate new job",
		initialJobs: []job{
			{id: "job1", priority: 1, cpu: 4, memory: 8192, disk: 500},
			{id: "job2", priority: 1, cpu: 8, memory: 16384, disk: 1000},
			{id: "job3", priority: 1, cpu: 4, memory: 8192, disk: 500},
		},
		jobsToRelease: []string{"job1"},
		secondaryJobs: []job{
			{id: "job4", priority: 1, cpu: 4, memory: 8192, disk: 500},
		},
		expectedInitialAlloc: map[string]string{
			"job1": "node1",
			"job2": "node2",
			"job3": "node3",
		},
		expectedFinalAlloc: map[string]string{
			"job2": "node2",
			"job3": "node3",
			"job4": "node1", // job4 should be allocated to the resources freed by job1
		},
	},
}

var invalidAllocationTestCases = []struct {
	description string
	job         job
	expectError bool
}{
	{
		description: "Job requesting more resources than any node has",
		job: job{
			id:       "bigJob",
			priority: 1,
			cpu:      100,
			memory:   1000000,
			disk:     10000,
		},
		expectError: true,
	},
}

type job struct {
	id             string
	priority       int
	cpu            int
	memory         int
	disk           int
	preferredNodes []string
}