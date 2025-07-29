package traffic_routing

import (
	"errors"
	"math"
)

type edge struct {
	to       int
	capacity int
	flow     int
}

func RouteTraffic(n int, edges []Edge, requests []Request) ([]map[string]interface{}, error) {
	// Build adjacency list representation
	graph := make([][]edge, n)
	for _, e := range edges {
		graph[e.From] = append(graph[e.From], edge{
			to:       e.To,
			capacity: e.Capacity,
			flow:     e.Flow,
		})
	}

	result := make([]map[string]interface{}, 0, len(requests))

	for _, req := range requests {
		if req.Source == req.Dest {
			// Handle case where source and destination are same
			res := map[string]interface{}{
				"paths": []PathFlow{
					{Path: []int{req.Source}, Flow: req.Demand},
				},
			}
			result = append(result, res)
			continue
		}

		// Find all possible paths from source to destination
		paths := findAllPaths(graph, req.Source, req.Dest)
		if len(paths) == 0 {
			return nil, errors.New("no path found for request")
		}

		// Calculate remaining capacities for edges
		remainingCap := make(map[[2]int]int)
		for u := 0; u < n; u++ {
			for _, e := range graph[u] {
				remainingCap[[2]int{u, e.to}] = e.capacity - e.flow
			}
		}

		// Distribute flow among paths to minimize max congestion
		allocations, err := allocateFlow(paths, remainingCap, req.Demand)
		if err != nil {
			return nil, err
		}

		// Prepare result for this request
		pathFlows := make([]PathFlow, 0)
		for i, path := range paths {
			if allocations[i] > 0 {
				pathFlows = append(pathFlows, PathFlow{
					Path: path,
					Flow: allocations[i],
				})
			}
		}

		result = append(result, map[string]interface{}{
			"paths": pathFlows,
		})
	}

	return result, nil
}

func findAllPaths(graph [][]edge, src, dst int) [][]int {
	var paths [][]int
	visited := make([]bool, len(graph))
	currentPath := []int{src}
	findPathsDFS(graph, src, dst, visited, &currentPath, &paths)
	return paths
}

func findPathsDFS(graph [][]edge, u, dst int, visited []bool, currentPath *[]int, paths *[][]int) {
	if u == dst {
		path := make([]int, len(*currentPath))
		copy(path, *currentPath)
		*paths = append(*paths, path)
		return
	}

	visited[u] = true
	for _, e := range graph[u] {
		if !visited[e.to] {
			*currentPath = append(*currentPath, e.to)
			findPathsDFS(graph, e.to, dst, visited, currentPath, paths)
			*currentPath = (*currentPath)[:len(*currentPath)-1]
		}
	}
	visited[u] = false
}

func allocateFlow(paths [][]int, remainingCap map[[2]int]int, demand int) ([]int, error) {
	if len(paths) == 0 {
		return nil, errors.New("no paths available")
	}

	// Simple proportional allocation based on path capacities
	pathCapacities := make([]int, len(paths))
	for i, path := range paths {
		minCap := math.MaxInt32
		for j := 0; j < len(path)-1; j++ {
			u, v := path[j], path[j+1]
			cap := remainingCap[[2]int{u, v}]
			if cap < minCap {
				minCap = cap
			}
		}
		pathCapacities[i] = minCap
	}

	totalCapacity := 0
	for _, cap := range pathCapacities {
		totalCapacity += cap
	}

	if totalCapacity < demand {
		return nil, errors.New("insufficient capacity for demand")
	}

	allocations := make([]int, len(paths))
	remainingDemand := demand

	// First pass: allocate proportionally
	for i := range paths {
		if totalCapacity > 0 {
			alloc := (demand * pathCapacities[i]) / totalCapacity
			allocations[i] = alloc
			remainingDemand -= alloc
		}
	}

	// Second pass: distribute remaining demand
	for i := 0; i < remainingDemand; i++ {
		allocations[i%len(allocations)]++
	}

	return allocations, nil
}