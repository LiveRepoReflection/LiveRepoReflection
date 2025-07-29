package network_orchestrator

import (
	"bufio"
	"strconv"
	"strings"
	"sync"
)

type Request struct {
	ID         int
	Source     int
	Destination int
	Payload    string
}

type Response struct {
	RequestID int
	Success   bool
	Path      []int
}

type Network struct {
	adjacency map[int][]int
	capacity  map[[2]int]int
	mu        sync.Mutex
}

func parseTopology(topology string) *Network {
	network := &Network{
		adjacency: make(map[int][]int),
		capacity:  make(map[[2]int]int),
	}

	scanner := bufio.NewScanner(strings.NewReader(topology))
	for scanner.Scan() {
		line := scanner.Text()
		if line == "" {
			continue
		}

		parts := strings.Split(line, ":")
		if len(parts) != 2 {
			continue
		}

		source, err := strconv.Atoi(parts[0])
		if err != nil {
			continue
		}

		neighbors := strings.Split(parts[1], ",")
		for _, neighbor := range neighbors {
			neighbor = strings.TrimSpace(neighbor)
			if neighbor == "" {
				continue
			}

			dest, err := strconv.Atoi(neighbor)
			if err != nil {
				continue
			}

			network.adjacency[source] = append(network.adjacency[source], dest)
			network.capacity[[2]int{source, dest}] = 1
			network.capacity[[2]int{dest, source}] = 1
		}
	}

	return network
}

func (n *Network) findPath(source, destination int) []int {
	visited := make(map[int]bool)
	queue := [][]int{{source}}
	visited[source] = true

	for len(queue) > 0 {
		path := queue[0]
		queue = queue[1:]
		current := path[len(path)-1]

		if current == destination {
			return path
		}

		for _, neighbor := range n.adjacency[current] {
			if !visited[neighbor] {
				visited[neighbor] = true
				newPath := make([]int, len(path))
				copy(newPath, path)
				newPath = append(newPath, neighbor)
				queue = append(queue, newPath)
			}
		}
	}

	return nil
}

func (n *Network) reservePath(path []int) bool {
	n.mu.Lock()
	defer n.mu.Unlock()

	for i := 0; i < len(path)-1; i++ {
		from := path[i]
		to := path[i+1]
		key := [2]int{from, to}
		if n.capacity[key] <= 0 {
			return false
		}
	}

	for i := 0; i < len(path)-1; i++ {
		from := path[i]
		to := path[i+1]
		key := [2]int{from, to}
		n.capacity[key]--
		reverseKey := [2]int{to, from}
		n.capacity[reverseKey]--
	}

	return true
}

func (n *Network) releasePath(path []int) {
	n.mu.Lock()
	defer n.mu.Unlock()

	for i := 0; i < len(path)-1; i++ {
		from := path[i]
		to := path[i+1]
		key := [2]int{from, to}
		n.capacity[key]++
		reverseKey := [2]int{to, from}
		n.capacity[reverseKey]++
	}
}

func Orchestrate(topology string, requests []Request) []Response {
	network := parseTopology(topology)
	responses := make([]Response, len(requests))

	for i, req := range requests {
		path := network.findPath(req.Source, req.Destination)
		if path == nil {
			responses[i] = Response{
				RequestID: req.ID,
				Success:   false,
				Path:      nil,
			}
			continue
		}

		if !network.reservePath(path) {
			responses[i] = Response{
				RequestID: req.ID,
				Success:   false,
				Path:      nil,
			}
			continue
		}

		responses[i] = Response{
			RequestID: req.ID,
			Success:   true,
			Path:      path,
		}

		// In a real system, we'd release the path after processing is complete
		// For this implementation, we'll keep it reserved
	}

	return responses
}