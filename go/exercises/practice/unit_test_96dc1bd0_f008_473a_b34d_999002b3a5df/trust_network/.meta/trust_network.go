package trust_network

import (
	"errors"
	"math"
)

type TrustNetwork struct {
	users      map[string]bool
	trustEdges map[string]map[string]float64
}

func NewTrustNetwork() *TrustNetwork {
	return &TrustNetwork{
		users:      make(map[string]bool),
		trustEdges: make(map[string]map[string]float64),
	}
}

func (tn *TrustNetwork) AddUser(userID string) {
	tn.users[userID] = true
}

func (tn *TrustNetwork) HasUser(userID string) bool {
	return tn.users[userID]
}

func (tn *TrustNetwork) AddTrustEdge(fromUserID, toUserID string, trustScore float64) error {
	if !tn.HasUser(fromUserID) || !tn.HasUser(toUserID) {
		return errors.New("user does not exist")
	}

	if trustScore < 0.0 || trustScore > 1.0 {
		return errors.New("trust score must be between 0.0 and 1.0")
	}

	if tn.trustEdges[fromUserID] == nil {
		tn.trustEdges[fromUserID] = make(map[string]float64)
	}
	tn.trustEdges[fromUserID][toUserID] = trustScore

	return nil
}

func (tn *TrustNetwork) GetTrustworthiness(userID string) float64 {
	if !tn.HasUser(userID) {
		return 0.0
	}

	var sum float64
	var count int

	for fromUser := range tn.trustEdges {
		if trustScore, exists := tn.trustEdges[fromUser][userID]; exists {
			sum += trustScore
			count++
		}
	}

	if count == 0 {
		return 0.0
	}
	return sum / float64(count)
}

func (tn *TrustNetwork) FindBestTrustPath(fromUserID, toUserID string) []string {
	if !tn.HasUser(fromUserID) || !tn.HasUser(toUserID) {
		return nil
	}

	type path struct {
		nodes []string
		score float64
	}

	visited := make(map[string]bool)
	queue := []path{{nodes: []string{fromUserID}, score: 1.0}}
	var bestPath path

	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]

		lastNode := current.nodes[len(current.nodes)-1]
		if lastNode == toUserID {
			if current.score > bestPath.score || 
				(math.Abs(current.score-bestPath.score) < 1e-9 && len(current.nodes) < len(bestPath.nodes)) {
				bestPath = current
			}
			continue
		}

		if visited[lastNode] {
			continue
		}
		visited[lastNode] = true

		for neighbor, trust := range tn.trustEdges[lastNode] {
			newPath := path{
				nodes: append([]string{}, current.nodes...),
				score: current.score * trust,
			}
			newPath.nodes = append(newPath.nodes, neighbor)
			queue = append(queue, newPath)
		}
	}

	return bestPath.nodes
}

func (tn *TrustNetwork) GetUsersInCycles() []string {
	visited := make(map[string]bool)
	recStack := make(map[string]bool)
	cycleUsers := make(map[string]bool)

	for user := range tn.users {
		if !visited[user] {
			tn.detectCycles(user, visited, recStack, cycleUsers)
		}
	}

	result := make([]string, 0, len(cycleUsers))
	for user := range cycleUsers {
		result = append(result, user)
	}
	return result
}

func (tn *TrustNetwork) detectCycles(user string, visited, recStack, cycleUsers map[string]bool) bool {
	visited[user] = true
	recStack[user] = true

	for neighbor := range tn.trustEdges[user] {
		if !visited[neighbor] {
			if tn.detectCycles(neighbor, visited, recStack, cycleUsers) {
				cycleUsers[user] = true
				return true
			}
		} else if recStack[neighbor] {
			cycleUsers[user] = true
			return true
		}
	}

	recStack[user] = false
	return false
}