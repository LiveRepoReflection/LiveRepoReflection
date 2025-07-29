package taskscheduler

import (
	"container/heap"
	"math"
)

// Task represents a single task with its properties
type Task struct {
	ID           int
	Duration     int
	Deadline     int
	Dependencies []int
}

// taskNode represents a task in the scheduling graph
type taskNode struct {
	task       Task
	inDegree   int
	startTime  int
	completed  bool
	dependents []int
}

// priorityQueue implements heap.Interface and holds taskNodes
type priorityQueue []*taskNode

func (pq priorityQueue) Len() int           { return len(pq) }
func (pq priorityQueue) Less(i, j int) bool { return pq[i].task.Deadline < pq[j].task.Deadline }
func (pq priorityQueue) Swap(i, j int)      { pq[i], pq[j] = pq[j], pq[i] }
func (pq *priorityQueue) Push(x interface{}) { *pq = append(*pq, x.(*taskNode)) }
func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

// ScheduleTasks determines the optimal order of task execution
func ScheduleTasks(tasks []Task) ([]int, int, bool) {
	if len(tasks) == 0 {
		return []int{}, 0, true
	}

	// Create graph representation
	graph := make(map[int]*taskNode)
	for _, task := range tasks {
		graph[task.ID] = &taskNode{
			task:       task,
			inDegree:   len(task.Dependencies),
			startTime:  0,
			completed:  false,
			dependents: make([]int, 0),
		}
	}

	// Build dependency graph
	for _, task := range tasks {
		for _, depID := range task.Dependencies {
			graph[depID].dependents = append(graph[depID].dependents, task.ID)
		}
	}

	// Check for cycles using DFS
	visited := make(map[int]bool)
	inStack := make(map[int]bool)
	
	var hasCycle func(int) bool
	hasCycle = func(nodeID int) bool {
		visited[nodeID] = true
		inStack[nodeID] = true
		
		for _, depID := range graph[nodeID].task.Dependencies {
			if !visited[depID] {
				if hasCycle(depID) {
					return true
				}
			} else if inStack[depID] {
				return true
			}
		}
		
		inStack[nodeID] = false
		return false
	}

	for id := range graph {
		if !visited[id] {
			if hasCycle(id) {
				return []int{}, 0, false
			}
		}
	}

	// Initialize priority queue with tasks that have no dependencies
	pq := make(priorityQueue, 0)
	for id, node := range graph {
		if node.inDegree == 0 {
			heap.Push(&pq, graph[id])
		}
	}

	schedule := make([]int, 0, len(tasks))
	currentTime := 0
	maxSpan := 0

	// Schedule tasks using modified Kahn's algorithm with deadline priority
	for pq.Len() > 0 {
		node := heap.Pop(&pq).(*taskNode)
		
		// Check if deadline can be met
		if currentTime + node.task.Duration > node.task.Deadline {
			return []int{}, 0, false
		}

		// Schedule the task
		schedule = append(schedule, node.task.ID)
		node.startTime = currentTime
		node.completed = true
		currentTime += node.task.Duration
		maxSpan = int(math.Max(float64(maxSpan), float64(currentTime)))

		// Update dependencies
		for _, depID := range node.dependents {
			dep := graph[depID]
			dep.inDegree--
			if dep.inDegree == 0 {
				heap.Push(&pq, dep)
			}
		}
	}

	// Check if all tasks were scheduled
	if len(schedule) != len(tasks) {
		return []int{}, 0, false
	}

	return schedule, maxSpan, true
}