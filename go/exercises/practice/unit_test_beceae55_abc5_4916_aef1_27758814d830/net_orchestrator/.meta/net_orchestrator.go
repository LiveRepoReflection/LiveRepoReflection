package net_orchestrator

import (
	"errors"
	"sync"
)

type NetworkOrchestrator struct {
	mu     sync.RWMutex
	graph  map[string]map[string]int
}

func NewNetworkOrchestrator() *NetworkOrchestrator {
	return &NetworkOrchestrator{
		graph: make(map[string]map[string]int),
	}
}

func (no *NetworkOrchestrator) AddVM(vmID string) error {
	no.mu.Lock()
	defer no.mu.Unlock()

	if _, exists := no.graph[vmID]; exists {
		return errors.New("VM already exists")
	}

	no.graph[vmID] = make(map[string]int)
	return nil
}

func (no *NetworkOrchestrator) RemoveVM(vmID string) error {
	no.mu.Lock()
	defer no.mu.Unlock()

	if _, exists := no.graph[vmID]; !exists {
		return errors.New("VM does not exist")
	}

	// Remove all links to this VM
	for neighbor := range no.graph[vmID] {
		delete(no.graph[neighbor], vmID)
	}

	delete(no.graph, vmID)
	return nil
}

func (no *NetworkOrchestrator) AddLink(vmID1, vmID2 string, bandwidth int) error {
	no.mu.Lock()
	defer no.mu.Unlock()

	if _, exists := no.graph[vmID1]; !exists {
		return errors.New("VM1 does not exist")
	}
	if _, exists := no.graph[vmID2]; !exists {
		return errors.New("VM2 does not exist")
	}

	no.graph[vmID1][vmID2] = bandwidth
	no.graph[vmID2][vmID1] = bandwidth
	return nil
}

func (no *NetworkOrchestrator) RemoveLink(vmID1, vmID2 string) error {
	no.mu.Lock()
	defer no.mu.Unlock()

	if _, exists := no.graph[vmID1]; !exists {
		return errors.New("VM1 does not exist")
	}
	if _, exists := no.graph[vmID2]; !exists {
		return errors.New("VM2 does not exist")
	}
	if _, exists := no.graph[vmID1][vmID2]; !exists {
		return errors.New("Link does not exist")
	}

	delete(no.graph[vmID1], vmID2)
	delete(no.graph[vmID2], vmID1)
	return nil
}

func (no *NetworkOrchestrator) UpdateLinkBandwidth(vmID1, vmID2 string, newBandwidth int) error {
	no.mu.Lock()
	defer no.mu.Unlock()

	if _, exists := no.graph[vmID1]; !exists {
		return errors.New("VM1 does not exist")
	}
	if _, exists := no.graph[vmID2]; !exists {
		return errors.New("VM2 does not exist")
	}
	if _, exists := no.graph[vmID1][vmID2]; !exists {
		return errors.New("Link does not exist")
	}

	no.graph[vmID1][vmID2] = newBandwidth
	no.graph[vmID2][vmID1] = newBandwidth
	return nil
}

func (no *NetworkOrchestrator) FindMaxBandwidthPath(vmID1, vmID2 string) []string {
	no.mu.RLock()
	defer no.mu.RUnlock()

	if _, exists := no.graph[vmID1]; !exists {
		return nil
	}
	if _, exists := no.graph[vmID2]; !exists {
		return nil
	}

	if vmID1 == vmID2 {
		return []string{vmID1}
	}

	// Modified Dijkstra's algorithm to find path with maximum minimum bandwidth
	visited := make(map[string]bool)
	prev := make(map[string]string)
	minBandwidth := make(map[string]int)
	queue := make([]string, 0)

	for vm := range no.graph {
		minBandwidth[vm] = -1
	}
	minBandwidth[vmID1] = 1 << 30 // Start with "infinite" bandwidth
	queue = append(queue, vmID1)

	for len(queue) > 0 {
		// Find VM with maximum minBandwidth in queue
		maxIdx := 0
		for i := 1; i < len(queue); i++ {
			if minBandwidth[queue[i]] > minBandwidth[queue[maxIdx]] {
				maxIdx = i
			}
		}
		current := queue[maxIdx]
		queue = append(queue[:maxIdx], queue[maxIdx+1:]...)

		if current == vmID2 {
			break
		}

		if visited[current] {
			continue
		}
		visited[current] = true

		for neighbor, bw := range no.graph[current] {
			if !visited[neighbor] {
				newMin := bw
				if minBandwidth[current] < bw {
					newMin = minBandwidth[current]
				}

				if newMin > minBandwidth[neighbor] {
					minBandwidth[neighbor] = newMin
					prev[neighbor] = current
					queue = append(queue, neighbor)
				}
			}
		}
	}

	// Reconstruct path if one exists
	if _, exists := prev[vmID2]; !exists {
		return nil
	}

	path := make([]string, 0)
	current := vmID2
	for current != vmID1 {
		path = append([]string{current}, path...)
		current = prev[current]
	}
	path = append([]string{vmID1}, path...)

	return path
}