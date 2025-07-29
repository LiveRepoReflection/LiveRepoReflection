package decentralized_routing

import (
	"container/list"
)

type Follower struct {
	ID     string
	Server string
}

type User struct {
	Followers []Follower
}

type Server struct {
	Connections []string
	Users       map[string]User
}

type NetworkState struct {
	Servers map[string]Server
}

type MessagePath struct {
	ServerID string
	Path     []string
}

func RouteMessage(originServerID string, userID string, message string, networkState NetworkState) map[string][]string {
	result := make(map[string][]string)
	visited := make(map[string]bool)
	queue := list.New()

	// Initialize with origin server
	queue.PushBack(MessagePath{
		ServerID: originServerID,
		Path:     []string{originServerID},
	})
	visited[originServerID] = true

	// Get all target servers that host followers
	targetServers := make(map[string]bool)
	if server, ok := networkState.Servers[originServerID]; ok {
		if user, ok := server.Users[userID]; ok {
			for _, follower := range user.Followers {
				targetServers[follower.Server] = true
			}
		}
	}

	// BFS to find paths to all reachable servers
	for queue.Len() > 0 {
		elem := queue.Front()
		queue.Remove(elem)
		current := elem.Value.(MessagePath)

		// If this server hosts followers, record the path
		if targetServers[current.ServerID] {
			result[current.ServerID] = current.Path
		}

		// Explore all connected servers
		if server, ok := networkState.Servers[current.ServerID]; ok {
			for _, neighbor := range server.Connections {
				if !visited[neighbor] {
					visited[neighbor] = true
					newPath := make([]string, len(current.Path))
					copy(newPath, current.Path)
					newPath = append(newPath, neighbor)
					queue.PushBack(MessagePath{
						ServerID: neighbor,
						Path:     newPath,
					})
				}
			}
		}
	}

	return result
}