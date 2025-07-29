package socialfeed

import (
	"container/heap"
	"fmt"
	"sync"
	"time"
)

// SocialFeed represents the main social feed system
type SocialFeed struct {
	users       map[int64]*User
	posts       map[int64][]*Post
	postCache   *PostCache
	mutex       sync.RWMutex
}

// User represents a user in the system
type User struct {
	ID        int64
	Following map[int64]bool
}

// PostCache implements a simple LRU cache for posts
type PostCache struct {
	capacity int
	cache    map[int64][]Post
	lru      []int64
	mutex    sync.RWMutex
}

// PostHeap is a min-heap of Posts ordered by timestamp
type PostHeap []Post

func (h PostHeap) Len() int           { return len(h) }
func (h PostHeap) Less(i, j int) bool { return h[i].Timestamp > h[j].Timestamp }
func (h PostHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *PostHeap) Push(x interface{}) {
	*h = append(*h, x.(Post))
}
func (h *PostHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

// NewSocialFeed creates a new instance of SocialFeed
func NewSocialFeed() *SocialFeed {
	return &SocialFeed{
		users:     make(map[int64]*User),
		posts:     make(map[int64][]*Post),
		postCache: newPostCache(1000), // Cache capacity of 1000 users
	}
}

// newPostCache creates a new post cache with given capacity
func newPostCache(capacity int) *PostCache {
	return &PostCache{
		capacity: capacity,
		cache:    make(map[int64][]Post),
		lru:      make([]int64, 0),
	}
}

// AddUser adds a new user to the system
func (sf *SocialFeed) AddUser(userID int64) error {
	sf.mutex.Lock()
	defer sf.mutex.Unlock()

	if _, exists := sf.users[userID]; exists {
		return fmt.Errorf("user %d already exists", userID)
	}

	sf.users[userID] = &User{
		ID:        userID,
		Following: make(map[int64]bool),
	}
	return nil
}

// AddFollower creates a follower relationship between users
func (sf *SocialFeed) AddFollower(userID, targetID int64) error {
	sf.mutex.Lock()
	defer sf.mutex.Unlock()

	user, exists := sf.users[userID]
	if !exists {
		return fmt.Errorf("user %d does not exist", userID)
	}

	if _, exists := sf.users[targetID]; !exists {
		return fmt.Errorf("target user %d does not exist", targetID)
	}

	user.Following[targetID] = true
	
	// Invalidate cache for the user
	sf.postCache.invalidate(userID)
	return nil
}

// CreatePost creates a new post
func (sf *SocialFeed) CreatePost(userID int64, content string, timestamp, likes int64) error {
	sf.mutex.Lock()
	defer sf.mutex.Unlock()

	if _, exists := sf.users[userID]; !exists {
		return fmt.Errorf("user %d does not exist", userID)
	}

	post := &Post{
		UserID:    userID,
		Content:   content,
		Timestamp: timestamp,
		Likes:     likes,
	}

	sf.posts[userID] = append(sf.posts[userID], post)

	// Invalidate cache for all followers
	for uid, user := range sf.users {
		if user.Following[userID] {
			sf.postCache.invalidate(uid)
		}
	}

	return nil
}

// GetUserFeed retrieves a user's feed
func (sf *SocialFeed) GetUserFeed(userID int64, offset, limit int) ([]Post, error) {
	sf.mutex.RLock()
	defer sf.mutex.RUnlock()

	user, exists := sf.users[userID]
	if !exists {
		return nil, fmt.Errorf("user %d does not exist", userID)
	}

	// Check cache first
	if cached := sf.postCache.get(userID); cached != nil {
		end := offset + limit
		if end > len(cached) {
			end = len(cached)
		}
		if offset >= end {
			return []Post{}, nil
		}
		return cached[offset:end], nil
	}

	// If not in cache, generate feed
	var allPosts PostHeap
	heap.Init(&allPosts)

	// Collect posts from all followed users
	for followedID := range user.Following {
		for _, post := range sf.posts[followedID] {
			heap.Push(&allPosts, *post)
		}
	}

	// Convert heap to sorted slice
	result := make([]Post, 0, allPosts.Len())
	for allPosts.Len() > 0 {
		post := heap.Pop(&allPosts).(Post)
		result = append(result, post)
	}

	// Cache the result
	sf.postCache.set(userID, result)

	// Apply offset and limit
	end := offset + limit
	if end > len(result) {
		end = len(result)
	}
	if offset >= end {
		return []Post{}, nil
	}
	return result[offset:end], nil
}

// Cache operations
func (pc *PostCache) get(userID int64) []Post {
	pc.mutex.RLock()
	defer pc.mutex.RUnlock()

	if posts, exists := pc.cache[userID]; exists {
		return posts
	}
	return nil
}

func (pc *PostCache) set(userID int64, posts []Post) {
	pc.mutex.Lock()
	defer pc.mutex.Unlock()

	if len(pc.cache) >= pc.capacity {
		// Remove least recently used
		delete(pc.cache, pc.lru[0])
		pc.lru = pc.lru[1:]
	}

	pc.cache[userID] = posts
	pc.lru = append(pc.lru, userID)
}

func (pc *PostCache) invalidate(userID int64) {
	pc.mutex.Lock()
	defer pc.mutex.Unlock()

	delete(pc.cache, userID)
	// Remove from LRU
	for i, id := range pc.lru {
		if id == userID {
			pc.lru = append(pc.lru[:i], pc.lru[i+1:]...)
			break
		}
	}
}

// Additional helper function for production environment
func (sf *SocialFeed) cleanup() {
	// Periodically clean up old posts
	ticker := time.NewTicker(24 * time.Hour)
	go func() {
		for range ticker.C {
			sf.mutex.Lock()
			cutoff := time.Now().Add(-30 * 24 * time.Hour).Unix() // 30 days
			for userID, posts := range sf.posts {
				newPosts := make([]*Post, 0)
				for _, post := range posts {
					if post.Timestamp > cutoff {
						newPosts = append(newPosts, post)
					}
				}
				sf.posts[userID] = newPosts
			}
			sf.mutex.Unlock()
		}
	}()
}