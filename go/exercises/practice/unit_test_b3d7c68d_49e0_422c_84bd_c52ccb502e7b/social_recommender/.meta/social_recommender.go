package social_recommender

import (
	"sync"
	"sort"
)

type SocialGraph struct {
	mu             sync.RWMutex
	users          map[string]*User
	connections    map[string]map[string]bool
}

type User struct {
	interests map[string]bool
}

func NewSocialGraph() *SocialGraph {
	return &SocialGraph{
		users:       make(map[string]*User),
		connections: make(map[string]map[string]bool),
	}
}

func (sg *SocialGraph) AddUser(userID string, interests []string) {
	sg.mu.Lock()
	defer sg.mu.Unlock()

	if _, exists := sg.users[userID]; exists {
		return
	}

	user := &User{
		interests: make(map[string]bool),
	}
	for _, interest := range interests {
		user.interests[interest] = true
	}

	sg.users[userID] = user
	sg.connections[userID] = make(map[string]bool)
}

func (sg *SocialGraph) RemoveUser(userID string) {
	sg.mu.Lock()
	defer sg.mu.Unlock()

	if _, exists := sg.users[userID]; !exists {
		return
	}

	delete(sg.users, userID)
	delete(sg.connections, userID)

	for source := range sg.connections {
		delete(sg.connections[source], userID)
	}
}

func (sg *SocialGraph) Connect(userID1, userID2 string) {
	sg.mu.Lock()
	defer sg.mu.Unlock()

	if _, exists := sg.users[userID1]; !exists {
		return
	}
	if _, exists := sg.users[userID2]; !exists {
		return
	}

	sg.connections[userID1][userID2] = true
}

func (sg *SocialGraph) Disconnect(userID1, userID2 string) {
	sg.mu.Lock()
	defer sg.mu.Unlock()

	if _, exists := sg.connections[userID1]; !exists {
		return
	}

	delete(sg.connections[userID1], userID2)
}

func (sg *SocialGraph) IsConnected(source, target string) bool {
	sg.mu.RLock()
	defer sg.mu.RUnlock()

	if connections, exists := sg.connections[source]; exists {
		return connections[target]
	}
	return false
}

func (sg *SocialGraph) GetSize() int {
	sg.mu.RLock()
	defer sg.mu.RUnlock()
	return len(sg.users)
}

func (sg *SocialGraph) GetRecommendations(userID string, maxRecommendations int) []string {
	sg.mu.RLock()
	defer sg.mu.RUnlock()

	if _, exists := sg.users[userID]; !exists {
		return nil
	}

	currentUser := sg.users[userID]
	directConnections := sg.connections[userID]
	allConnections := sg.getAllConnections(userID)

	candidates := make(map[string]struct {
		sharedInterests int
		distance        int
	})

	for candidateID, candidate := range sg.users {
		if candidateID == userID {
			continue
		}
		if _, connected := allConnections[candidateID]; connected {
			continue
		}

		shared := 0
		for interest := range candidate.interests {
			if currentUser.interests[interest] {
				shared++
			}
		}

		distance := sg.getConnectionDistance(userID, candidateID, directConnections)

		if shared > 0 || distance <= 2 {
			candidates[candidateID] = struct {
				sharedInterests int
				distance        int
			}{shared, distance}
		}
	}

	type recommendation struct {
		userID          string
		sharedInterests int
		distance        int
	}

	var recs []recommendation
	for userID, stats := range candidates {
		recs = append(recs, recommendation{
			userID:          userID,
			sharedInterests: stats.sharedInterests,
			distance:        stats.distance,
		})
	}

	sort.Slice(recs, func(i, j int) bool {
		if recs[i].sharedInterests != recs[j].sharedInterests {
			return recs[i].sharedInterests > recs[j].sharedInterests
		}
		if recs[i].distance != recs[j].distance {
			return recs[i].distance < recs[j].distance
		}
		return recs[i].userID < recs[j].userID
	})

	result := make([]string, 0, maxRecommendations)
	for i := 0; i < len(recs) && i < maxRecommendations; i++ {
		result = append(result, recs[i].userID)
	}

	return result
}

func (sg *SocialGraph) getAllConnections(userID string) map[string]bool {
	connections := make(map[string]bool)
	for target := range sg.connections[userID] {
		connections[target] = true
	}
	for source := range sg.connections {
		if sg.connections[source][userID] {
			connections[source] = true
		}
	}
	return connections
}

func (sg *SocialGraph) getConnectionDistance(source, target string, directConnections map[string]bool) int {
	if directConnections[target] {
		return 1
	}

	visited := make(map[string]bool)
	queue := []string{source}
	distance := 1

	for len(queue) > 0 {
		nextLevel := make([]string, 0)
		distance++

		for _, current := range queue {
			if visited[current] {
				continue
			}
			visited[current] = true

			for neighbor := range sg.connections[current] {
				if neighbor == target {
					return distance
				}
				if !visited[neighbor] {
					nextLevel = append(nextLevel, neighbor)
				}
			}
		}

		queue = nextLevel
	}

	return 3 // More than 2 degrees of separation
}