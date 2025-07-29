package social_analytics

import (
	"errors"
	"math"
	"sort"
	"sync"
)

var (
	ErrUserAlreadyExists = errors.New("user already exists")
	ErrUserNotFound      = errors.New("user not found")
)

type User struct {
	id          int
	metadata    string
	connections map[int]struct{}
}

type SocialGraph struct {
	mu    sync.RWMutex
	users map[int]*User
}

type UserPageRank struct {
	UserID int
	Score  float64
}

func NewSocialGraph() *SocialGraph {
	return &SocialGraph{
		users: make(map[int]*User),
	}
}

func (sg *SocialGraph) IngestUser(userID int, metadata string) error {
	sg.mu.Lock()
	defer sg.mu.Unlock()
	if _, exists := sg.users[userID]; exists {
		return ErrUserAlreadyExists
	}
	sg.users[userID] = &User{
		id:          userID,
		metadata:    metadata,
		connections: make(map[int]struct{}),
	}
	return nil
}

func (sg *SocialGraph) IngestConnection(userID1, userID2 int) error {
	sg.mu.Lock()
	defer sg.mu.Unlock()
	user1, ok1 := sg.users[userID1]
	user2, ok2 := sg.users[userID2]
	if !ok1 || !ok2 {
		return ErrUserNotFound
	}
	if _, exists := user1.connections[userID2]; !exists {
		user1.connections[userID2] = struct{}{}
	}
	if _, exists := user2.connections[userID1]; !exists {
		user2.connections[userID1] = struct{}{}
	}
	return nil
}

func (sg *SocialGraph) GetDegreeDistribution() map[int]int {
	sg.mu.RLock()
	defer sg.mu.RUnlock()
	distribution := make(map[int]int)
	for _, user := range sg.users {
		distribution[user.id] = len(user.connections)
	}
	return distribution
}

func (sg *SocialGraph) GetConnectedComponents() int {
	sg.mu.RLock()
	defer sg.mu.RUnlock()
	visited := make(map[int]bool)
	count := 0
	for id := range sg.users {
		if !visited[id] {
			dfs(sg.users, id, visited)
			count++
		}
	}
	return count
}

func dfs(users map[int]*User, start int, visited map[int]bool) {
	stack := []int{start}
	for len(stack) > 0 {
		node := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if visited[node] {
			continue
		}
		visited[node] = true
		for neigh := range users[node].connections {
			if !visited[neigh] {
				stack = append(stack, neigh)
			}
		}
	}
}

func (sg *SocialGraph) GetPersonalizedPageRank(sourceUserID int, k int) ([]UserPageRank, error) {
	sg.mu.RLock()
	if _, exists := sg.users[sourceUserID]; !exists {
		sg.mu.RUnlock()
		return nil, ErrUserNotFound
	}
	// Copy the users to work with a consistent snapshot
	usersCopy := make(map[int]*User, len(sg.users))
	for id, user := range sg.users {
		usersCopy[id] = user
	}
	sg.mu.RUnlock()

	const dampingFactor = 0.85
	const teleportation = 0.15
	// Initialize ranks
	rank := make(map[int]float64)
	for id := range usersCopy {
		rank[id] = 0.0
	}
	rank[sourceUserID] = 1.0

	iterations := 20
	for i := 0; i < iterations; i++ {
		newRank := make(map[int]float64)
		for id := range usersCopy {
			if id == sourceUserID {
				newRank[id] = teleportation
			} else {
				newRank[id] = 0.0
			}
		}
		for id, user := range usersCopy {
			outDegree := float64(len(user.connections))
			if outDegree == 0 {
				// Distribute rank evenly if dangling node
				for uid := range newRank {
					newRank[uid] += dampingFactor * rank[id] / float64(len(usersCopy))
				}
			} else {
				for neighbor := range user.connections {
					newRank[neighbor] += dampingFactor * rank[id] / outDegree
				}
			}
		}
		diff := 0.0
		for id := range rank {
			diff += math.Abs(newRank[id] - rank[id])
		}
		rank = newRank
		if diff < 1e-6 {
			break
		}
	}

	results := make([]UserPageRank, 0, len(rank))
	for id, score := range rank {
		results = append(results, UserPageRank{
			UserID: id,
			Score:  score,
		})
	}
	sort.Slice(results, func(i, j int) bool {
		if results[i].Score == results[j].Score {
			return results[i].UserID < results[j].UserID
		}
		return results[i].Score > results[j].Score
	})
	if k > len(results) {
		k = len(results)
	}
	return results[:k], nil
}