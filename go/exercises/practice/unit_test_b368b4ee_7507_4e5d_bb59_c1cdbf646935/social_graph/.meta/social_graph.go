package social_graph

import (
    "errors"
    "sort"
    "sync"
)

var (
    ErrInvalidUserID    = errors.New("invalid user ID")
    ErrInvalidOffset    = errors.New("invalid offset")
    ErrInvalidLimit     = errors.New("invalid limit")
    ErrSelfFollow       = errors.New("cannot follow self")
)

type SocialGraph struct {
    // Using RWMutex for better concurrent read performance
    mu sync.RWMutex
    
    // Using maps for O(1) lookup performance
    // followers maps a user to their followers
    followers map[uint64]map[uint64]struct{}
    
    // following maps a user to who they follow
    following map[uint64]map[uint64]struct{}
}

func NewSocialGraph() *SocialGraph {
    return &SocialGraph{
        followers: make(map[uint64]map[uint64]struct{}),
        following: make(map[uint64]map[uint64]struct{}),
    }
}

func (sg *SocialGraph) Follow(followerID, followeeID uint64) error {
    if followerID == 0 || followeeID == 0 {
        return ErrInvalidUserID
    }
    
    if followerID == followeeID {
        return ErrSelfFollow
    }
    
    sg.mu.Lock()
    defer sg.mu.Unlock()
    
    // Initialize maps if they don't exist
    if sg.followers[followeeID] == nil {
        sg.followers[followeeID] = make(map[uint64]struct{})
    }
    if sg.following[followerID] == nil {
        sg.following[followerID] = make(map[uint64]struct{})
    }
    
    // Add the relationship
    sg.followers[followeeID][followerID] = struct{}{}
    sg.following[followerID][followeeID] = struct{}{}
    
    return nil
}

func (sg *SocialGraph) Unfollow(followerID, followeeID uint64) error {
    if followerID == 0 || followeeID == 0 {
        return ErrInvalidUserID
    }
    
    sg.mu.Lock()
    defer sg.mu.Unlock()
    
    // Remove the relationship if it exists
    if sg.followers[followeeID] != nil {
        delete(sg.followers[followeeID], followerID)
    }
    if sg.following[followerID] != nil {
        delete(sg.following[followerID], followeeID)
    }
    
    return nil
}

func (sg *SocialGraph) IsFollowing(followerID, followeeID uint64) (bool, error) {
    if followerID == 0 || followeeID == 0 {
        return false, ErrInvalidUserID
    }
    
    sg.mu.RLock()
    defer sg.mu.RUnlock()
    
    if following, exists := sg.following[followerID]; exists {
        _, isFollowing := following[followeeID]
        return isFollowing, nil
    }
    
    return false, nil
}

func (sg *SocialGraph) GetFollowers(userID uint64, offset, limit int) ([]uint64, error) {
    if userID == 0 {
        return nil, ErrInvalidUserID
    }
    if offset < 0 {
        return nil, ErrInvalidOffset
    }
    if limit <= 0 {
        return nil, ErrInvalidLimit
    }
    
    sg.mu.RLock()
    defer sg.mu.RUnlock()
    
    followers := make([]uint64, 0)
    if userFollowers, exists := sg.followers[userID]; exists {
        for followerID := range userFollowers {
            followers = append(followers, followerID)
        }
    }
    
    // Sort for consistent results
    sort.Slice(followers, func(i, j int) bool {
        return followers[i] < followers[j]
    })
    
    // Handle pagination
    if offset >= len(followers) {
        return []uint64{}, nil
    }
    
    end := offset + limit
    if end > len(followers) {
        end = len(followers)
    }
    
    return followers[offset:end], nil
}

func (sg *SocialGraph) GetFollowees(userID uint64, offset, limit int) ([]uint64, error) {
    if userID == 0 {
        return nil, ErrInvalidUserID
    }
    if offset < 0 {
        return nil, ErrInvalidOffset
    }
    if limit <= 0 {
        return nil, ErrInvalidLimit
    }
    
    sg.mu.RLock()
    defer sg.mu.RUnlock()
    
    followees := make([]uint64, 0)
    if userFollowing, exists := sg.following[userID]; exists {
        for followeeID := range userFollowing {
            followees = append(followees, followeeID)
        }
    }
    
    // Sort for consistent results
    sort.Slice(followees, func(i, j int) bool {
        return followees[i] < followees[j]
    })
    
    // Handle pagination
    if offset >= len(followees) {
        return []uint64{}, nil
    }
    
    end := offset + limit
    if end > len(followees) {
        end = len(followees)
    }
    
    return followees[offset:end], nil
}

func (sg *SocialGraph) GetMutualFollowees(userID, otherUserID uint64, offset, limit int) ([]uint64, error) {
    if userID == 0 || otherUserID == 0 {
        return nil, ErrInvalidUserID
    }
    if offset < 0 {
        return nil, ErrInvalidOffset
    }
    if limit <= 0 {
        return nil, ErrInvalidLimit
    }
    
    sg.mu.RLock()
    defer sg.mu.RUnlock()
    
    // Get both users' followees
    userFollowing := sg.following[userID]
    otherFollowing := sg.following[otherUserID]
    
    // Find mutual followees
    mutuals := make([]uint64, 0)
    for followeeID := range userFollowing {
        if _, exists := otherFollowing[followeeID]; exists {
            mutuals = append(mutuals, followeeID)
        }
    }
    
    // Sort for consistent results
    sort.Slice(mutuals, func(i, j int) bool {
        return mutuals[i] < mutuals[j]
    })
    
    // Handle pagination
    if offset >= len(mutuals) {
        return []uint64{}, nil
    }
    
    end := offset + limit
    if end > len(mutuals) {
        end = len(mutuals)
    }
    
    return mutuals[offset:end], nil
}