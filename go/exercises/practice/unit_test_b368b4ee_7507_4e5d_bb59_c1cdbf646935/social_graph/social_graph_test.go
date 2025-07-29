package social_graph

import (
    "reflect"
    "testing"
)

type Operation struct {
    Type        string
    FollowerID  uint64
    FolloweeID  uint64
    UserID      uint64
    OtherUserID uint64
    Offset      int
    Limit       int
}

type Result struct {
    Success     bool
    IsFollowing bool
    Users       []uint64
    Error       error
}

func TestSocialGraph(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            graph := NewSocialGraph()
            
            for i, op := range tc.operations {
                var result Result
                
                switch op.Type {
                case "Follow":
                    err := graph.Follow(op.FollowerID, op.FolloweeID)
                    result = Result{Success: err == nil, Error: err}
                
                case "Unfollow":
                    err := graph.Unfollow(op.FollowerID, op.FolloweeID)
                    result = Result{Success: err == nil, Error: err}
                
                case "IsFollowing":
                    following, err := graph.IsFollowing(op.FollowerID, op.FolloweeID)
                    result = Result{Success: err == nil, IsFollowing: following, Error: err}
                
                case "GetFollowers":
                    followers, err := graph.GetFollowers(op.UserID, op.Offset, op.Limit)
                    result = Result{Success: err == nil, Users: followers, Error: err}
                
                case "GetFollowees":
                    followees, err := graph.GetFollowees(op.UserID, op.Offset, op.Limit)
                    result = Result{Success: err == nil, Users: followees, Error: err}
                
                case "GetMutualFollowees":
                    mutuals, err := graph.GetMutualFollowees(op.UserID, op.OtherUserID, op.Offset, op.Limit)
                    result = Result{Success: err == nil, Users: mutuals, Error: err}
                }
                
                expected := tc.expected[i]
                
                if result.Success != expected.Success {
                    t.Errorf("Operation %d: expected success=%v, got=%v", i, expected.Success, result.Success)
                }
                
                if result.IsFollowing != expected.IsFollowing {
                    t.Errorf("Operation %d: expected isFollowing=%v, got=%v", i, expected.IsFollowing, result.IsFollowing)
                }
                
                if !reflect.DeepEqual(result.Users, expected.Users) {
                    t.Errorf("Operation %d: expected users=%v, got=%v", i, expected.Users, result.Users)
                }
            }
        })
    }
}

func BenchmarkSocialGraph(b *testing.B) {
    graph := NewSocialGraph()
    
    for i := 0; i < b.N; i++ {
        followerID := uint64(i % 1000)
        followeeID := uint64((i + 1) % 1000)
        
        _ = graph.Follow(followerID, followeeID)
        _, _ = graph.GetFollowers(followeeID, 0, 10)
        _, _ = graph.GetFollowees(followerID, 0, 10)
        _, _ = graph.IsFollowing(followerID, followeeID)
        _ = graph.Unfollow(followerID, followeeID)
    }
}