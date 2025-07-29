package resource_network_test

import (
	"fmt"
	"sync"
	"testing"
	"time"

	"resource_network"
)

// waitForTaskStatus polls the task status until it matches the expected status or the timeout is reached.
func waitForTaskStatus(net *resource_network.Network, taskID string, desiredStatus string, timeout time.Duration) bool {
	start := time.Now()
	for {
		status, err := net.GetTaskStatus(taskID)
		if err != nil {
			return false
		}
		if status == desiredStatus {
			return true
		}
		if time.Since(start) > timeout {
			return false
		}
		time.Sleep(10 * time.Millisecond)
	}
}

func TestBasicAllocation(t *testing.T) {
	net := resource_network.NewNetwork()

	// Register two nodes with adequate resources.
	node1 := &resource_network.Node{ID: "node1", CPU: 4, Memory: 8, Storage: 100}
	node2 := &resource_network.Node{ID: "node2", CPU: 4, Memory: 8, Storage: 100}
	net.RegisterNode(node1)
	net.RegisterNode(node2)

	// Submit a task with moderate resource requirements.
	task := resource_network.Task{
		CPU:     2,
		Memory:  4,
		Storage: 20,
		Priority: 1,
	}
	taskID, err := net.SubmitTask(task)
	if err != nil {
		t.Fatalf("Failed to submit task: %v", err)
	}

	// Wait for the task to complete.
	if !waitForTaskStatus(net, taskID, "completed", 2*time.Second) {
		t.Fatalf("Task %s did not complete within the expected time", taskID)
	}
}

func TestNodeFailure(t *testing.T) {
	net := resource_network.NewNetwork()

	// Register nodes in the network.
	node1 := &resource_network.Node{ID: "node1", CPU: 4, Memory: 8, Storage: 100}
	node2 := &resource_network.Node{ID: "node2", CPU: 4, Memory: 8, Storage: 100}
	net.RegisterNode(node1)
	net.RegisterNode(node2)

	// Submit a task that will take a bit longer to process.
	task := resource_network.Task{
		CPU:     3,
		Memory:  6,
		Storage: 50,
		Priority: 2,
	}
	taskID, err := net.SubmitTask(task)
	if err != nil {
		t.Fatalf("Failed to submit task: %v", err)
	}

	// Wait a short period to ensure the task has been assigned.
	time.Sleep(100 * time.Millisecond)

	// Identify the node to which the task was allocated.
	assignedNodeID, err := net.GetTaskAssignedNode(taskID)
	if err != nil {
		t.Fatalf("Error retrieving assigned node for task %s: %v", taskID, err)
	}

	// Simulate failure of the assigned node.
	net.FailNode(assignedNodeID)

	// Wait for the task to be reassigned and eventually completed.
	if !waitForTaskStatus(net, taskID, "completed", 3*time.Second) {
		t.Fatalf("Task %s did not complete after node failure", taskID)
	}
}

func TestConcurrentTaskSubmission(t *testing.T) {
	net := resource_network.NewNetwork()

	// Register multiple nodes to handle concurrent task submissions.
	numNodes := 5
	for i := 0; i < numNodes; i++ {
		node := &resource_network.Node{
			ID:      fmt.Sprintf("node%d", i+1),
			CPU:     4,
			Memory:  8,
			Storage: 100,
		}
		net.RegisterNode(node)
	}

	// Submit multiple tasks concurrently.
	numTasks := 20
	var wg sync.WaitGroup
	taskIDs := make([]string, numTasks)
	errors := make([]error, numTasks)

	for i := 0; i < numTasks; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			task := resource_network.Task{
				CPU:     1,
				Memory:  2,
				Storage: 10,
				Priority: 1,
			}
			taskID, err := net.SubmitTask(task)
			if err == nil {
				// Wait for the task to complete.
				if !waitForTaskStatus(net, taskID, "completed", 2*time.Second) {
					err = fmt.Errorf("task %s did not complete", taskID)
				}
			}
			taskIDs[i] = taskID
			errors[i] = err
		}(i)
	}
	wg.Wait()

	for i, err := range errors {
		if err != nil {
			t.Errorf("Error in task %d (%s): %v", i, taskIDs[i], err)
		}
	}
}

func TestInvalidTaskSubmission(t *testing.T) {
	net := resource_network.NewNetwork()

	// Register a node with limited resources.
	node := &resource_network.Node{ID: "node1", CPU: 2, Memory: 4, Storage: 10}
	net.RegisterNode(node)

	// Submit a task that exceeds the node's resource capacities.
	task := resource_network.Task{
		CPU:     5,
		Memory:  10,
		Storage: 20,
		Priority: 1,
	}
	taskID, err := net.SubmitTask(task)
	if err == nil {
		// If the submission is accepted, the task should eventually fail.
		if !waitForTaskStatus(net, taskID, "failed", 2*time.Second) {
			t.Fatalf("Task %s requiring excessive resources did not fail as expected", taskID)
		}
	}
}