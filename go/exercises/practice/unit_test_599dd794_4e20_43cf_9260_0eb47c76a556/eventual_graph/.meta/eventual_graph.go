package eventual_graph

import (
	"errors"
	"sync"
)

type Node struct {
	ID      string
	Version int
	Data    string
}

var (
	ErrNodeNotFound      = errors.New("node not found")
	ErrMaxNodesExceeded  = errors.New("max nodes to send exceeded")
	ErrInvalidParameters = errors.New("invalid parameters")
)

func FindNeighbors(graph map[string]Node, edges map[string][]string, nodeID string) []string {
	if neighbors, exists := edges[nodeID]; exists {
		return neighbors
	}
	return nil
}

func PropagateUpdates(graph map[string]Node, edges map[string][]string, sourceNodeID string, targetNodeID string, maxNodesToSend int) error {
	if maxNodesToSend <= 0 {
		return ErrInvalidParameters
	}

	mu := &sync.Mutex{}
	mu.Lock()
	defer mu.Unlock()

	if _, exists := graph[sourceNodeID]; !exists {
		return ErrNodeNotFound
	}
	if _, exists := graph[targetNodeID]; !exists {
		return ErrNodeNotFound
	}

	visited := make(map[string]bool)
	queue := []string{sourceNodeID}
	nodesSent := 0

	for len(queue) > 0 && nodesSent < maxNodesToSend {
		currentNodeID := queue[0]
		queue = queue[1:]

		if visited[currentNodeID] {
			continue
		}
		visited[currentNodeID] = true

		sourceNode := graph[currentNodeID]
		targetNode := graph[targetNodeID]

		if sourceNode.Version > targetNode.Version {
			graph[targetNodeID] = Node{
				ID:      targetNode.ID,
				Version: sourceNode.Version,
				Data:    sourceNode.Data,
			}
			nodesSent++
		}

		if nodesSent >= maxNodesToSend {
			return ErrMaxNodesExceeded
		}

		for _, neighborID := range FindNeighbors(graph, edges, currentNodeID) {
			if !visited[neighborID] {
				queue = append(queue, neighborID)
			}
		}
	}

	return nil
}