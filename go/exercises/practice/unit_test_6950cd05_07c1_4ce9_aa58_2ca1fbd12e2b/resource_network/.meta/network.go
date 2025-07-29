package resource_network

import (
	"errors"
	"fmt"
	"sync"
	"time"
)

type Node struct {
	ID               string
	CPU              int
	Memory           int
	Storage          int
	Active           bool
	availableCPU     int
	availableMemory  int
	availableStorage int
}

type Task struct {
	ID           string
	CPU          int
	Memory       int
	Storage      int
	Priority     int
	Status       string // "pending", "running", "completed", "failed"
	AssignedNode string
}

type Network struct {
	mu         sync.Mutex
	nodes      map[string]*Node
	tasks      map[string]*Task
	nextTaskID int
}

func NewNetwork() *Network {
	return &Network{
		nodes: make(map[string]*Node),
		tasks: make(map[string]*Task),
	}
}

func (nw *Network) RegisterNode(node *Node) {
	nw.mu.Lock()
	defer nw.mu.Unlock()
	node.Active = true
	node.availableCPU = node.CPU
	node.availableMemory = node.Memory
	node.availableStorage = node.Storage
	nw.nodes[node.ID] = node
}

func (nw *Network) SubmitTask(task Task) (string, error) {
	nw.mu.Lock()
	taskID := fmt.Sprintf("task_%d", nw.nextTaskID)
	nw.nextTaskID++
	t := &Task{
		ID:       taskID,
		CPU:      task.CPU,
		Memory:   task.Memory,
		Storage:  task.Storage,
		Priority: task.Priority,
		Status:   "pending",
	}
	nw.tasks[taskID] = t
	nw.mu.Unlock()

	go nw.attemptAssign(t)
	return taskID, nil
}

func (nw *Network) attemptAssign(t *Task) {
	assigned := false
	deadline := time.Now().Add(500 * time.Millisecond)
	for time.Now().Before(deadline) {
		nw.mu.Lock()
		if t.Status == "pending" {
			if nw.assignTask(t) {
				assigned = true
				nw.mu.Unlock()
				break
			}
		}
		nw.mu.Unlock()
		time.Sleep(50 * time.Millisecond)
	}
	nw.mu.Lock()
	if !assigned && t.Status == "pending" {
		t.Status = "failed"
	}
	nw.mu.Unlock()
	if assigned {
		// Simulate task execution
		time.Sleep(100 * time.Millisecond)
		nw.mu.Lock()
		if t.Status == "running" {
			t.Status = "completed"
			node := nw.nodes[t.AssignedNode]
			if node != nil {
				node.availableCPU += t.CPU
				node.availableMemory += t.Memory
				node.availableStorage += t.Storage
			}
		}
		nw.mu.Unlock()
	}
}

func (nw *Network) assignTask(t *Task) bool {
	for _, node := range nw.nodes {
		if node.Active && node.availableCPU >= t.CPU && node.availableMemory >= t.Memory && node.availableStorage >= t.Storage {
			t.AssignedNode = node.ID
			node.availableCPU -= t.CPU
			node.availableMemory -= t.Memory
			node.availableStorage -= t.Storage
			t.Status = "running"
			return true
		}
	}
	return false
}

func (nw *Network) GetTaskStatus(taskID string) (string, error) {
	nw.mu.Lock()
	defer nw.mu.Unlock()
	if task, ok := nw.tasks[taskID]; ok {
		return task.Status, nil
	}
	return "", errors.New("task not found")
}

func (nw *Network) GetTaskAssignedNode(taskID string) (string, error) {
	nw.mu.Lock()
	defer nw.mu.Unlock()
	if task, ok := nw.tasks[taskID]; ok {
		if task.AssignedNode == "" {
			return "", errors.New("task not assigned to any node")
		}
		return task.AssignedNode, nil
	}
	return "", errors.New("task not found")
}

func (nw *Network) FailNode(nodeID string) {
	nw.mu.Lock()
	node, exists := nw.nodes[nodeID]
	if !exists {
		nw.mu.Unlock()
		return
	}
	node.Active = false
	// For all tasks running on the failed node, mark them as pending and restore the allocated resources.
	for _, t := range nw.tasks {
		if t.AssignedNode == nodeID && t.Status == "running" {
			node.availableCPU += t.CPU
			node.availableMemory += t.Memory
			node.availableStorage += t.Storage
			t.Status = "pending"
			t.AssignedNode = ""
		}
	}
	nw.mu.Unlock()
	nw.schedulePendingTasks()
}

func (nw *Network) schedulePendingTasks() {
	nw.mu.Lock()
	pendingTasks := []*Task{}
	for _, t := range nw.tasks {
		if t.Status == "pending" {
			pendingTasks = append(pendingTasks, t)
		}
	}
	nw.mu.Unlock()
	for _, t := range pendingTasks {
		go nw.attemptAssign(t)
	}
}