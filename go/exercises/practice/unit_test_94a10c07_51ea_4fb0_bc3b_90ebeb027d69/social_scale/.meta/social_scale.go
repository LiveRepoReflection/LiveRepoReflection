package social_scale

import (
	"errors"
	"sort"
	"sync"
)

type User struct {
	id        string
	followers map[string]struct{}
	following map[string]struct{}
}

type SocialGraph struct {
	mutex sync.RWMutex
	users map[string]*User
}

// NewSocialGraph creates and returns a new SocialGraph.
func NewSocialGraph() *SocialGraph {
	return &SocialGraph{
		users: make(map[string]*User),
	}
}

// AddUser adds a new user with the given userID.
func (sg *SocialGraph) AddUser(userID string) error {
	sg.mutex.Lock()
	defer sg.mutex.Unlock()

	if _, exists := sg.users[userID]; exists {
		return errors.New("user already exists")
	}

	sg.users[userID] = &User{
		id:        userID,
		followers: make(map[string]struct{}),
		following: make(map[string]struct{}),
	}
	return nil
}

// RemoveUser removes the user with the given userID and cleans up related connections.
func (sg *SocialGraph) RemoveUser(userID string) error {
	sg.mutex.Lock()
	defer sg.mutex.Unlock()

	u, exists := sg.users[userID]
	if !exists {
		return errors.New("user does not exist")
	}

	// Remove the user from their followers' following lists.
	for followerID := range u.followers {
		if follower, ok := sg.users[followerID]; ok {
			delete(follower.following, userID)
		}
	}
	// Remove the user from their followees' followers lists.
	for followeeID := range u.following {
		if followee, ok := sg.users[followeeID]; ok {
			delete(followee.followers, userID)
		}
	}
	delete(sg.users, userID)
	return nil
}

// Follow makes followerID follow followeeID.
func (sg *SocialGraph) Follow(followerID, followeeID string) error {
	sg.mutex.Lock()
	defer sg.mutex.Unlock()

	if followerID == followeeID {
		return errors.New("cannot follow self")
	}

	follower, existsFollower := sg.users[followerID]
	followee, existsFollowee := sg.users[followeeID]
	if !existsFollower || !existsFollowee {
		return errors.New("user does not exist")
	}

	// Check if already following.
	if _, exists := follower.following[followeeID]; exists {
		return errors.New("already following")
	}

	follower.following[followeeID] = struct{}{}
	followee.followers[followerID] = struct{}{}
	return nil
}

// Unfollow makes followerID unfollow followeeID.
func (sg *SocialGraph) Unfollow(followerID, followeeID string) error {
	sg.mutex.Lock()
	defer sg.mutex.Unlock()

	follower, existsFollower := sg.users[followerID]
	followee, existsFollowee := sg.users[followeeID]
	if !existsFollower || !existsFollowee {
		return errors.New("user does not exist")
	}

	if _, exists := follower.following[followeeID]; !exists {
		return errors.New("not following")
	}

	delete(follower.following, followeeID)
	delete(followee.followers, followerID)
	return nil
}

// GetFollowers returns the list of followers for the given userID, sorted lexicographically.
func (sg *SocialGraph) GetFollowers(userID string) ([]string, error) {
	sg.mutex.RLock()
	defer sg.mutex.RUnlock()

	user, exists := sg.users[userID]
	if !exists {
		return nil, errors.New("user does not exist")
	}

	var followers []string
	for followerID := range user.followers {
		followers = append(followers, followerID)
	}
	sort.Strings(followers)
	return followers, nil
}

// GetFollowing returns the list of users that the given userID is following, sorted lexicographically.
func (sg *SocialGraph) GetFollowing(userID string) ([]string, error) {
	sg.mutex.RLock()
	defer sg.mutex.RUnlock()

	user, exists := sg.users[userID]
	if !exists {
		return nil, errors.New("user does not exist")
	}

	var following []string
	for followeeID := range user.following {
		following = append(following, followeeID)
	}
	sort.Strings(following)
	return following, nil
}

// MutualFollowers returns the list of userIDs who follow both userID1 and userID2, sorted lexicographically.
func (sg *SocialGraph) MutualFollowers(userID1, userID2 string) ([]string, error) {
	sg.mutex.RLock()
	defer sg.mutex.RUnlock()

	user1, exists1 := sg.users[userID1]
	user2, exists2 := sg.users[userID2]
	if !exists1 || !exists2 {
		return nil, errors.New("user does not exist")
	}

	var mutual []string
	// Iterate through the smaller set of followers for efficiency.
	if len(user1.followers) < len(user2.followers) {
		for followerID := range user1.followers {
			if _, ok := user2.followers[followerID]; ok {
				mutual = append(mutual, followerID)
			}
		}
	} else {
		for followerID := range user2.followers {
			if _, ok := user1.followers[followerID]; ok {
				mutual = append(mutual, followerID)
			}
		}
	}
	sort.Strings(mutual)
	return mutual, nil
}

// SuggestFriends returns up to N friend suggestions for the specified user.
// A suggestion is valid if the candidate is followed by at least K of the user's followings,
// is not already followed by the user, and is not the user themselves.
// Suggestions are sorted primarily by the number of mutual followings in descending order,
// and then lexicographically by userID in case of ties.
func (sg *SocialGraph) SuggestFriends(userID string, K int, N int) ([]string, error) {
	sg.mutex.RLock()
	defer sg.mutex.RUnlock()

	user, exists := sg.users[userID]
	if !exists {
		return nil, errors.New("user does not exist")
	}

	// Map to count how many of user's followings follow candidate user.
	candidateCount := make(map[string]int)

	// Iterate over each user that the current user is following.
	for followeeID := range user.following {
		followee, exists := sg.users[followeeID]
		if !exists {
			continue
		}
		// For each user that followee is following, count as potential candidate.
		for candidateID := range followee.following {
			// Skip if candidate is the current user or is already followed.
			if candidateID == userID {
				continue
			}
			if _, alreadyFollowing := user.following[candidateID]; alreadyFollowing {
				continue
			}
			candidateCount[candidateID]++
		}
	}

	// Filter candidates who meet the threshold K.
	type candidateInfo struct {
		id    string
		count int
	}
	var candidates []candidateInfo
	for candidate, count := range candidateCount {
		if count >= K {
			candidates = append(candidates, candidateInfo{
				id:    candidate,
				count: count,
			})
		}
	}

	// Sort candidates by count in descending order and then lexicographically.
	sort.Slice(candidates, func(i, j int) bool {
		if candidates[i].count == candidates[j].count {
			return candidates[i].id < candidates[j].id
		}
		return candidates[i].count > candidates[j].count
	})

	// Collect up to N candidate ids.
	var suggestions []string
	for i, candidate := range candidates {
		if i >= N {
			break
		}
		suggestions = append(suggestions, candidate.id)
	}

	return suggestions, nil
}