package social_network

import (
	"sort"
	"sync"
)

type SocialNetwork struct {
	users map[int]*user
	mu    sync.RWMutex
}

type user struct {
	friends map[int]struct{}
}

func NewSocialNetwork() *SocialNetwork {
	return &SocialNetwork{
		users: make(map[int]*user),
	}
}

func (sn *SocialNetwork) AddUser(userID int) {
	sn.mu.Lock()
	defer sn.mu.Unlock()

	if _, exists := sn.users[userID]; !exists {
		sn.users[userID] = &user{
			friends: make(map[int]struct{}),
		}
	}
}

func (sn *SocialNetwork) RemoveUser(userID int) {
	sn.mu.Lock()
	defer sn.mu.Unlock()

	if user, exists := sn.users[userID]; exists {
		// Remove this user from all friends' lists
		for friendID := range user.friends {
			if friend, friendExists := sn.users[friendID]; friendExists {
				delete(friend.friends, userID)
			}
		}
		delete(sn.users, userID)
	}
}

func (sn *SocialNetwork) Connect(userID1, userID2 int) {
	sn.mu.Lock()
	defer sn.mu.Unlock()

	user1, exists1 := sn.users[userID1]
	user2, exists2 := sn.users[userID2]

	if !exists1 || !exists2 || userID1 == userID2 {
		return
	}

	user1.friends[userID2] = struct{}{}
	user2.friends[userID1] = struct{}{}
}

func (sn *SocialNetwork) Disconnect(userID1, userID2 int) {
	sn.mu.Lock()
	defer sn.mu.Unlock()

	user1, exists1 := sn.users[userID1]
	user2, exists2 := sn.users[userID2]

	if !exists1 || !exists2 {
		return
	}

	delete(user1.friends, userID2)
	delete(user2.friends, userID1)
}

func (sn *SocialNetwork) GetFriends(userID int) []int {
	sn.mu.RLock()
	defer sn.mu.RUnlock()

	user, exists := sn.users[userID]
	if !exists {
		return nil
	}

	friends := make([]int, 0, len(user.friends))
	for friendID := range user.friends {
		friends = append(friends, friendID)
	}
	sort.Ints(friends)
	return friends
}

func (sn *SocialNetwork) GetMutualFriends(userID1, userID2 int) []int {
	sn.mu.RLock()
	defer sn.mu.RUnlock()

	user1, exists1 := sn.users[userID1]
	user2, exists2 := sn.users[userID2]

	if !exists1 || !exists2 {
		return nil
	}

	var mutual []int
	for friendID := range user1.friends {
		if _, isMutual := user2.friends[friendID]; isMutual {
			mutual = append(mutual, friendID)
		}
	}
	sort.Ints(mutual)
	return mutual
}

func (sn *SocialNetwork) GetShortestFriendshipPath(userID1, userID2 int) []int {
	sn.mu.RLock()
	defer sn.mu.RUnlock()

	if userID1 == userID2 {
		if _, exists := sn.users[userID1]; exists {
			return []int{userID1}
		}
		return nil
	}

	_, exists1 := sn.users[userID1]
	_, exists2 := sn.users[userID2]
	if !exists1 || !exists2 {
		return nil
	}

	visited := make(map[int]bool)
	queue := [][]int{{userID1}}
	visited[userID1] = true

	for len(queue) > 0 {
		path := queue[0]
		queue = queue[1:]
		current := path[len(path)-1]

		if current == userID2 {
			return path
		}

		for friend := range sn.users[current].friends {
			if !visited[friend] {
				visited[friend] = true
				newPath := make([]int, len(path)+1)
				copy(newPath, path)
				newPath[len(newPath)-1] = friend
				queue = append(queue, newPath)
			}
		}
	}

	return nil
}