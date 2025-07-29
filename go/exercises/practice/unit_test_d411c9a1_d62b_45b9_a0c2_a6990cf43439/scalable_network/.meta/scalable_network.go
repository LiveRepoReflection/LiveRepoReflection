package scalable_network

import (
	"errors"
	"sort"
	"sync"
	"time"
)

type User struct {
	ID          string
	Username    string
	ProfileText string
}

type Post struct {
	UserID    string
	Message   string
	Timestamp time.Time
}

type SocialNetwork struct {
	mu             sync.RWMutex
	users          map[string]User
	usernames      map[string]string
	friendships    map[string]map[string]struct{}
	posts          map[string][]Post
	userPostsCache map[string][]Post
}

func NewSocialNetwork() *SocialNetwork {
	return &SocialNetwork{
		users:          make(map[string]User),
		usernames:      make(map[string]string),
		friendships:    make(map[string]map[string]struct{}),
		posts:          make(map[string][]Post),
		userPostsCache: make(map[string][]Post),
	}
}

func (sn *SocialNetwork) CreateUser(username, profileText string) (string, error) {
	sn.mu.Lock()
	defer sn.mu.Unlock()

	if _, exists := sn.usernames[username]; exists {
		return "", errors.New("username already exists")
	}

	userID := generateUUID()
	user := User{
		ID:          userID,
		Username:    username,
		ProfileText: profileText,
	}

	sn.users[userID] = user
	sn.usernames[username] = userID
	sn.friendships[userID] = make(map[string]struct{})

	return userID, nil
}

func (sn *SocialNetwork) AddFriend(userID1, userID2 string) error {
	if userID1 == userID2 {
		return errors.New("cannot add self as friend")
	}

	sn.mu.Lock()
	defer sn.mu.Unlock()

	if _, exists := sn.users[userID1]; !exists {
		return errors.New("user1 does not exist")
	}
	if _, exists := sn.users[userID2]; !exists {
		return errors.New("user2 does not exist")
	}

	if _, exists := sn.friendships[userID1][userID2]; exists {
		return errors.New("friendship already exists")
	}

	sn.friendships[userID1][userID2] = struct{}{}
	sn.friendships[userID2][userID1] = struct{}{}

	return nil
}

func (sn *SocialNetwork) RemoveFriend(userID1, userID2 string) error {
	sn.mu.Lock()
	defer sn.mu.Unlock()

	if _, exists := sn.friendships[userID1][userID2]; !exists {
		return errors.New("friendship does not exist")
	}

	delete(sn.friendships[userID1], userID2)
	delete(sn.friendships[userID2], userID1)

	return nil
}

func (sn *SocialNetwork) PostMessage(userID, message string) error {
	sn.mu.Lock()
	defer sn.mu.Unlock()

	if _, exists := sn.users[userID]; !exists {
		return errors.New("user does not exist")
	}

	post := Post{
		UserID:    userID,
		Message:   message,
		Timestamp: time.Now(),
	}

	sn.posts[userID] = append(sn.posts[userID], post)
	sn.userPostsCache[userID] = append(sn.userPostsCache[userID], post)

	return nil
}

func (sn *SocialNetwork) GetNewsFeed(userID string, offset, pageSize int) ([]Post, error) {
	sn.mu.RLock()
	defer sn.mu.RUnlock()

	if _, exists := sn.users[userID]; !exists {
		return nil, errors.New("user does not exist")
	}

	if offset < 0 || pageSize <= 0 {
		return nil, errors.New("invalid pagination parameters")
	}

	var feed []Post
	for friendID := range sn.friendships[userID] {
		if posts, exists := sn.posts[friendID]; exists {
			feed = append(feed, posts...)
		}
	}

	sort.Slice(feed, func(i, j int) bool {
		return feed[i].Timestamp.After(feed[j].Timestamp)
	})

	start := offset
	end := offset + pageSize
	if start > len(feed) {
		return []Post{}, nil
	}
	if end > len(feed) {
		end = len(feed)
	}

	return feed[start:end], nil
}

func (sn *SocialNetwork) GetMutualFriends(userID1, userID2 string) ([]string, error) {
	sn.mu.RLock()
	defer sn.mu.RUnlock()

	if _, exists := sn.users[userID1]; !exists {
		return nil, errors.New("user1 does not exist")
	}
	if _, exists := sn.users[userID2]; !exists {
		return nil, errors.New("user2 does not exist")
	}

	var mutuals []string
	for friendID := range sn.friendships[userID1] {
		if _, exists := sn.friendships[userID2][friendID]; exists {
			mutuals = append(mutuals, friendID)
		}
	}

	return mutuals, nil
}

func generateUUID() string {
	return time.Now().Format("20060102150405") + "-" + randomString(8)
}

func randomString(n int) string {
	const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, n)
	for i := range b {
		b[i] = letters[time.Now().UnixNano()%int64(len(letters))]
	}
	return string(b)
}