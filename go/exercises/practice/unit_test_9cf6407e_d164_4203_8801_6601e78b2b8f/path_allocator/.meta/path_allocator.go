package path_allocator

import (
	"container/heap"
	"math"
)

type Path struct {
	nodes     []int
	minCap    int
	taskTotal int
	taskIndices []int
}

type PathHeap []Path

func (h PathHeap) Len() int           { return len(h) }
func (h PathHeap) Less(i, j int) bool { return h[i].taskTotal < h[j].taskTotal }
func (h PathHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *PathHeap) Push(x interface{}) {
	*h = append(*h, x.(Path))
}

func (h *PathHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

func AllocatePaths(graph map[int][]Edge, nodeCaps map[int]int, tasks []int, k int) [][]int {
	source := 0
	sink := findSink(graph)
	if sink == -1 {
		return nil
	}

	paths := findAllPaths(graph, source, sink)
	if len(paths) < k {
		return nil
	}

	pathHeap := initializePathHeap(paths, graph, nodeCaps)
	heap.Init(&pathHeap)

	taskHeap := make(TaskHeap, len(tasks))
	for i, size := range tasks {
		taskHeap[i] = Task{index: i, size: size}
	}
	heap.Init(&taskHeap)

	for taskHeap.Len() > 0 {
		task := heap.Pop(&taskHeap).(Task)
		assigned := false

		tempPaths := make([]Path, 0)
		for pathHeap.Len() > 0 {
			path := heap.Pop(&pathHeap).(Path)
			tempPaths = append(tempPaths, path)

			if canAssignTask(path, task.size, graph, nodeCaps) {
				path.taskTotal += task.size
				path.taskIndices = append(path.taskIndices, task.index)
				assigned = true
				break
			}
		}

		for _, p := range tempPaths {
			heap.Push(&pathHeap, p)
		}

		if !assigned {
			return nil
		}
	}

	result := make([][]int, k)
	for i := 0; i < k; i++ {
		path := heap.Pop(&pathHeap).(Path)
		result[i] = path.taskIndices
	}

	return result
}

func findSink(graph map[int][]Edge) int {
	maxNode := 0
	for node := range graph {
		if node > maxNode {
			maxNode = node
		}
	}

	for node := range graph {
		for _, edge := range graph[node] {
			if edge.To > maxNode {
				maxNode = edge.To
			}
		}
	}

	// Verify it's actually a sink (no outgoing edges)
	if _, exists := graph[maxNode]; exists {
		return -1
	}
	return maxNode
}

func findAllPaths(graph map[int][]Edge, source, sink int) [][]int {
	var paths [][]int
	var currentPath []int
	visited := make(map[int]bool)

	var dfs func(int)
	dfs = func(node int) {
		visited[node] = true
		currentPath = append(currentPath, node)

		if node == sink {
			pathCopy := make([]int, len(currentPath))
			copy(pathCopy, currentPath)
			paths = append(paths, pathCopy)
		} else {
			for _, edge := range graph[node] {
				if !visited[edge.To] {
					dfs(edge.To)
				}
			}
		}

		currentPath = currentPath[:len(currentPath)-1]
		visited[node] = false
	}

	dfs(source)
	return paths
}

func initializePathHeap(paths [][]int, graph map[int][]Edge, nodeCaps map[int]int) PathHeap {
	pathHeap := make(PathHeap, len(paths))
	for i, path := range paths {
		minCap := math.MaxInt32
		for _, node := range path {
			if nodeCaps[node] < minCap {
				minCap = nodeCaps[node]
			}
		}

		for j := 0; j < len(path)-1; j++ {
			for _, edge := range graph[path[j]] {
				if edge.To == path[j+1] && edge.Capacity < minCap {
					minCap = edge.Capacity
				}
			}
		}

		pathHeap[i] = Path{
			nodes:     path,
			minCap:    minCap,
			taskTotal: 0,
			taskIndices: []int{},
		}
	}
	return pathHeap
}

func canAssignTask(path Path, taskSize int, graph map[int][]Edge, nodeCaps map[int]int) bool {
	if path.taskTotal+taskSize > path.minCap {
		return false
	}

	// Check node capacities
	for _, node := range path.nodes {
		if nodeCaps[node] < path.taskTotal+taskSize {
			return false
		}
	}

	// Check edge capacities
	for i := 0; i < len(path.nodes)-1; i++ {
		from := path.nodes[i]
		to := path.nodes[i+1]
		for _, edge := range graph[from] {
			if edge.To == to && edge.Capacity < path.taskTotal+taskSize {
				return false
			}
		}
	}

	return true
}

type Task struct {
	index int
	size  int
}

type TaskHeap []Task

func (h TaskHeap) Len() int           { return len(h) }
func (h TaskHeap) Less(i, j int) bool { return h[i].size > h[j].size }
func (h TaskHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *TaskHeap) Push(x interface{}) {
	*h = append(*h, x.(Task))
}

func (h *TaskHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}