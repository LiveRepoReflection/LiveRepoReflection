package social_influence

import (
	"bufio"
	"fmt"
	"io"
	"sort"
	"strconv"
	"strings"
)

type Graph struct {
	adj map[string]map[string]bool
}

func NewGraph() *Graph {
	return &Graph{adj: make(map[string]map[string]bool)}
}

func (g *Graph) addEdge(u, v string) {
	if _, ok := g.adj[u]; !ok {
		g.adj[u] = make(map[string]bool)
	}
	if _, ok := g.adj[v]; !ok {
		g.adj[v] = make(map[string]bool)
	}
	g.adj[u][v] = true
	g.adj[v][u] = true
}

func (g *Graph) removeEdge(u, v string) {
	if _, ok := g.adj[u]; ok {
		delete(g.adj[u], v)
	}
	if _, ok := g.adj[v]; ok {
		delete(g.adj[v], u)
	}
}

func Process(r io.Reader, w io.Writer) error {
	scanner := bufio.NewScanner(r)
	graph := NewGraph()

	// Process network description.
	for scanner.Scan() {
		line := scanner.Text()
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) != 3 {
			continue
		}
		if parts[0] == "END" && parts[1] == "END" && parts[2] == "END" {
			break
		}
		user1, user2, op := parts[0], parts[1], parts[2]
		if op == "add" {
			graph.addEdge(user1, user2)
		} else if op == "remove" {
			graph.removeEdge(user1, user2)
		}
	}

	// Process analytical queries.
	for scanner.Scan() {
		line := scanner.Text()
		if line == "" {
			continue
		}
		parts := strings.Fields(line)
		if len(parts) != 4 {
			continue
		}
		if parts[0] == "END" {
			break
		}
		user := parts[0]
		influenceChange, err := strconv.ParseFloat(parts[1], 64)
		if err != nil {
			return err
		}
		propagationDepth, err := strconv.Atoi(parts[2])
		if err != nil {
			return err
		}
		decayFactor, err := strconv.ParseFloat(parts[3], 64)
		if err != nil {
			return err
		}

		// Propagate influence using BFS.
		// Each node gets influenceChange * (decayFactor^level) based on first visit.
		result := make(map[string]float64)
		type NodeLevel struct {
			name  string
			level int
		}
		queue := []NodeLevel{{name: user, level: 0}}
		visited := make(map[string]int)

		for len(queue) > 0 {
			cur := queue[0]
			queue = queue[1:]
			if lvl, ok := visited[cur.name]; ok && cur.level >= lvl {
				continue
			}
			visited[cur.name] = cur.level
			if cur.level <= propagationDepth {
				multiplier := 1.0
				for i := 0; i < cur.level; i++ {
					multiplier *= decayFactor
				}
				result[cur.name] = influenceChange * multiplier
				if cur.level < propagationDepth {
					neighbors, exists := graph.adj[cur.name]
					if exists {
						for neighbor := range neighbors {
							queue = append(queue, NodeLevel{name: neighbor, level: cur.level + 1})
						}
					}
				}
			}
		}

		// Sort and output results.
		var keys []string
		for k, v := range result {
			if v != 0 {
				keys = append(keys, k)
			}
		}
		sort.Strings(keys)
		for _, k := range keys {
			fmt.Fprintf(w, "%s:%.6f\n", k, result[k])
		}
	}

	if err := scanner.Err(); err != nil {
		return err
	}
	return nil
}