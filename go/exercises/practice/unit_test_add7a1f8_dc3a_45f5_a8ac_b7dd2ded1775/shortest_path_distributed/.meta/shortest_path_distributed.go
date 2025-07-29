package shortest_path_distributed

import (
	"sync"
)

type neighborFuncType func(node int64) []int64

var neighborFn neighborFuncType = func(node int64) []int64 {
	return []int64{}
}

// SetNeighborFunction allows the injection of a custom neighbor lookup function.
func SetNeighborFunction(fn neighborFuncType) {
	neighborFn = fn
}

// CalculateShortestPath finds the shortest path from startNode to endNode in a distributed graph
// using a level-by-level parallel Breadth-First Search (BFS).
func CalculateShortestPath(startNode, endNode int64) []int64 {
	if startNode == endNode {
		return []int64{startNode}
	}

	visited := make(map[int64]bool)
	prev := make(map[int64]int64)
	visited[startNode] = true

	currentLevel := []int64{startNode}
	found := false
	var mu sync.Mutex

	for len(currentLevel) > 0 && !found {
		var wg sync.WaitGroup
		nextLevel := []int64{}
		levelFound := false

		for _, node := range currentLevel {
			wg.Add(1)
			go func(n int64) {
				defer wg.Done()
				neighbors := neighborFn(n)
				if neighbors == nil {
					neighbors = []int64{}
				}
				for _, neighbor := range neighbors {
					mu.Lock()
					if !visited[neighbor] {
						visited[neighbor] = true
						prev[neighbor] = n
						nextLevel = append(nextLevel, neighbor)
						if neighbor == endNode {
							levelFound = true
						}
					}
					mu.Unlock()
				}
			}(node)
		}

		wg.Wait()
		if levelFound {
			found = true
			currentLevel = nextLevel
			break
		}
		currentLevel = nextLevel
	}

	if !visited[endNode] {
		return []int64{}
	}

	// Reconstruct the shortest path from endNode to startNode.
	path := []int64{}
	for at := endNode; ; {
		path = append([]int64{at}, path...)
		if at == startNode {
			break
		}
		at = prev[at]
	}
	return path
}