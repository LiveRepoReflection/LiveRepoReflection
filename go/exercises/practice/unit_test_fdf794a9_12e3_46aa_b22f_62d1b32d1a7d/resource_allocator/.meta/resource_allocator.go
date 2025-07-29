package resource_allocator

import (
	"container/heap"
	"fmt"
	"sort"
	"sync"
)

// ResourceAllocator represents the resource allocation system
type ResourceAllocator struct {
	nodes        map[string]*Node
	jobs         map[string]*Job
	waitingJobs  PriorityQueue
	assignedJobs map[string]string // jobID -> nodeID
	mu           sync.RWMutex
}

// Node represents a computing node with resources
type Node struct {
	ID            string
	TotalCPU      int
	TotalMemory   int
	TotalDisk     int
	AvailableCPU  int
	AvailableMemory int
	AvailableDisk int
	AssignedJobs  map[string]*Job
	mu            sync.RWMutex
}

// Job represents a computing job requiring resources
type Job struct {
	ID             string
	Priority       int
	CPU            int
	Memory         int
	Disk           int
	PreferredNodes []string
	Assigned       bool
	AssignedNodeID string
}

// ResourceStatus represents the current status of resources on a node
type ResourceStatus struct {
	TotalCPU       int
	TotalMemory    int
	TotalDisk      int
	UsedCPU        int
	UsedMemory     int
	UsedDisk       int
	AvailableCPU   int
	AvailableMemory int
	AvailableDisk  int
}

// PriorityQueue implements heap.Interface and holds Jobs
type PriorityQueue []*Job

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	// We want Pop to give us the highest priority job
	return pq[i].Priority > pq[j].Priority
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	job := x.(*Job)
	*pq = append(*pq, job)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	job := old[n-1]
	*pq = old[0 : n-1]
	return job
}

// NewResourceAllocator creates a new ResourceAllocator
func NewResourceAllocator() *ResourceAllocator {
	return &ResourceAllocator{
		nodes:        make(map[string]*Node),
		jobs:         make(map[string]*Job),
		waitingJobs:  make(PriorityQueue, 0),
		assignedJobs: make(map[string]string),
	}
}

// AddNode adds a new node to the cluster with the specified resources
func (ra *ResourceAllocator) AddNode(nodeID string, cpu, memory, disk int) error {
	ra.mu.Lock()
	defer ra.mu.Unlock()

	if _, exists := ra.nodes[nodeID]; exists {
		return fmt.Errorf("node with ID %s already exists", nodeID)
	}

	if cpu <= 0 || memory <= 0 || disk <= 0 {
		return fmt.Errorf("resources must be positive values")
	}

	ra.nodes[nodeID] = &Node{
		ID:              nodeID,
		TotalCPU:        cpu,
		TotalMemory:     memory,
		TotalDisk:       disk,
		AvailableCPU:    cpu,
		AvailableMemory: memory,
		AvailableDisk:   disk,
		AssignedJobs:    make(map[string]*Job),
	}

	return nil
}

// SubmitJob submits a new job to the system
func (ra *ResourceAllocator) SubmitJob(jobID string, priority, cpu, memory, disk int, preferredNodes []string) error {
	ra.mu.Lock()
	defer ra.mu.Unlock()

	if _, exists := ra.jobs[jobID]; exists {
		return fmt.Errorf("job with ID %s already exists", jobID)
	}

	if cpu <= 0 || memory <= 0 || disk <= 0 {
		return fmt.Errorf("resources must be positive values")
	}

	// Check if any node can fulfill this job's requirements
	canBeFulfilled := false
	for _, node := range ra.nodes {
		if node.TotalCPU >= cpu && node.TotalMemory >= memory && node.TotalDisk >= disk {
			canBeFulfilled = true
			break
		}
	}

	if !canBeFulfilled {
		return fmt.Errorf("job requires more resources than any single node possesses")
	}

	job := &Job{
		ID:             jobID,
		Priority:       priority,
		CPU:            cpu,
		Memory:         memory,
		Disk:           disk,
		PreferredNodes: preferredNodes,
		Assigned:       false,
	}

	ra.jobs[jobID] = job
	heap.Push(&ra.waitingJobs, job)

	return nil
}

// AllocateResources attempts to allocate resources to waiting jobs
func (ra *ResourceAllocator) AllocateResources() map[string]string {
	ra.mu.Lock()
	defer ra.mu.Unlock()

	result := make(map[string]string)

	// Make a copy of the waiting jobs queue to iterate through
	waitingJobs := make(PriorityQueue, len(ra.waitingJobs))
	copy(waitingJobs, ra.waitingJobs)

	// Sort by priority (highest first)
	sort.Sort(waitingJobs)

	// Process each waiting job
	for i := 0; i < len(waitingJobs); i++ {
		job := waitingJobs[i]
		
		// Skip jobs that are already assigned
		if job.Assigned {
			continue
		}

		// Try to allocate job to a preferred node first
		if job.PreferredNodes != nil && len(job.PreferredNodes) > 0 {
			allocated := false
			for _, nodeID := range job.PreferredNodes {
				node, exists := ra.nodes[nodeID]
				if !exists {
					continue
				}

				if ra.canNodeAccommodateJob(node, job) {
					ra.allocateJobToNode(job, node)
					result[job.ID] = node.ID
					allocated = true
					break
				}
			}

			if allocated {
				continue
			}
		}

		// If no preferred node is available or specified, find the best node
		bestNode := ra.findBestNodeForJob(job)
		if bestNode != nil {
			ra.allocateJobToNode(job, bestNode)
			result[job.ID] = bestNode.ID
		}
	}

	// Update the assigned jobs map
	for jobID, nodeID := range result {
		ra.assignedJobs[jobID] = nodeID
	}

	// Clean up the waiting jobs queue
	var newWaitingJobs PriorityQueue
	for _, job := range ra.waitingJobs {
		if !job.Assigned {
			newWaitingJobs = append(newWaitingJobs, job)
		}
	}
	ra.waitingJobs = newWaitingJobs
	heap.Init(&ra.waitingJobs)

	return result
}

// ReleaseResources releases resources allocated to a specific job
func (ra *ResourceAllocator) ReleaseResources(jobID string) error {
	ra.mu.Lock()
	defer ra.mu.Unlock()

	job, exists := ra.jobs[jobID]
	if !exists {
		return fmt.Errorf("job with ID %s does not exist", jobID)
	}

	if !job.Assigned {
		return fmt.Errorf("job with ID %s is not assigned to any node", jobID)
	}

	nodeID := job.AssignedNodeID
	node, exists := ra.nodes[nodeID]
	if !exists {
		return fmt.Errorf("node with ID %s does not exist", nodeID)
	}

	node.mu.Lock()
	defer node.mu.Unlock()

	node.AvailableCPU += job.CPU
	node.AvailableMemory += job.Memory
	node.AvailableDisk += job.Disk
	delete(node.AssignedJobs, jobID)

	job.Assigned = false
	job.AssignedNodeID = ""
	delete(ra.assignedJobs, jobID)

	// If the job still exists, add it back to the waiting queue
	if _, exists := ra.jobs[jobID]; exists {
		heap.Push(&ra.waitingJobs, job)
	}

	return nil
}

// GetNodeStatus returns the current resource utilization of a specific node
func (ra *ResourceAllocator) GetNodeStatus(nodeID string) (*ResourceStatus, error) {
	ra.mu.RLock()
	defer ra.mu.RUnlock()

	node, exists := ra.nodes[nodeID]
	if !exists {
		return nil, fmt.Errorf("node with ID %s does not exist", nodeID)
	}

	node.mu.RLock()
	defer node.mu.RUnlock()

	usedCPU := node.TotalCPU - node.AvailableCPU
	usedMemory := node.TotalMemory - node.AvailableMemory
	usedDisk := node.TotalDisk - node.AvailableDisk

	return &ResourceStatus{
		TotalCPU:        node.TotalCPU,
		TotalMemory:     node.TotalMemory,
		TotalDisk:       node.TotalDisk,
		UsedCPU:         usedCPU,
		UsedMemory:      usedMemory,
		UsedDisk:        usedDisk,
		AvailableCPU:    node.AvailableCPU,
		AvailableMemory: node.AvailableMemory,
		AvailableDisk:   node.AvailableDisk,
	}, nil
}

// canNodeAccommodateJob checks if a node can accommodate a job
func (ra *ResourceAllocator) canNodeAccommodateJob(node *Node, job *Job) bool {
	node.mu.RLock()
	defer node.mu.RUnlock()

	return node.AvailableCPU >= job.CPU &&
		node.AvailableMemory >= job.Memory &&
		node.AvailableDisk >= job.Disk
}

// allocateJobToNode allocates a job to a specific node
func (ra *ResourceAllocator) allocateJobToNode(job *Job, node *Node) {
	node.mu.Lock()
	defer node.mu.Unlock()

	node.AvailableCPU -= job.CPU
	node.AvailableMemory -= job.Memory
	node.AvailableDisk -= job.Disk
	node.AssignedJobs[job.ID] = job

	job.Assigned = true
	job.AssignedNodeID = node.ID
}

// findBestNodeForJob finds the best node for a job
func (ra *ResourceAllocator) findBestNodeForJob(job *Job) *Node {
	var bestNode *Node
	minRemaining := int(^uint(0) >> 1) // max int

	for _, node := range ra.nodes {
		if !ra.canNodeAccommodateJob(node, job) {
			continue
		}

		node.mu.RLock()
		// Calculate remaining resources after potential allocation
		remainingResources := node.AvailableCPU - job.CPU + 
			node.AvailableMemory - job.Memory + 
			node.AvailableDisk - job.Disk
		node.mu.RUnlock()

		// Choose the node that would have the least remaining resources
		// This helps to minimize fragmentation
		if remainingResources < minRemaining {
			minRemaining = remainingResources
			bestNode = node
		}
	}

	return bestNode
}

// GetAllJobs returns a copy of all jobs in the system
func (ra *ResourceAllocator) GetAllJobs() map[string]*Job {
	ra.mu.RLock()
	defer ra.mu.RUnlock()

	jobs := make(map[string]*Job, len(ra.jobs))
	for id, job := range ra.jobs {
		jobCopy := *job // Make a copy to avoid concurrent map access issues
		jobs[id] = &jobCopy
	}

	return jobs
}

// GetAssignedJobs returns a copy of the current job assignments
func (ra *ResourceAllocator) GetAssignedJobs() map[string]string {
	ra.mu.RLock()
	defer ra.mu.RUnlock()

	assigned := make(map[string]string, len(ra.assignedJobs))
	for jobID, nodeID := range ra.assignedJobs {
		assigned[jobID] = nodeID
	}

	return assigned
}

// RemoveJob removes a job from the system
func (ra *ResourceAllocator) RemoveJob(jobID string) error {
	ra.mu.Lock()
	defer ra.mu.Unlock()

	job, exists := ra.jobs[jobID]
	if !exists {
		return fmt.Errorf("job with ID %s does not exist", jobID)
	}

	// If the job is assigned, release resources first
	if job.Assigned {
		// We need to unlock to avoid deadlock since ReleaseResources will lock
		ra.mu.Unlock()
		err := ra.ReleaseResources(jobID)
		ra.mu.Lock()
		if err != nil {
			return err
		}
	}

	// Remove from waiting queue if present
	newWaitingJobs := make(PriorityQueue, 0, len(ra.waitingJobs))
	for _, j := range ra.waitingJobs {
		if j.ID != jobID {
			newWaitingJobs = append(newWaitingJobs, j)
		}
	}
	ra.waitingJobs = newWaitingJobs
	heap.Init(&ra.waitingJobs)

	// Delete from jobs map
	delete(ra.jobs, jobID)

	return nil
}