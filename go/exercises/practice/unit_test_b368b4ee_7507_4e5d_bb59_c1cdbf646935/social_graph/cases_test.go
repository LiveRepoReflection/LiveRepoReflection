package social_graph

// Test cases for the social graph implementation
var testCases = []struct {
    description string
    operations  []Operation
    expected    []Result
}{
    {
        description: "basic follow and check",
        operations: []Operation{
            {Type: "Follow", FollowerID: 1, FolloweeID: 2},
            {Type: "IsFollowing", FollowerID: 1, FolloweeID: 2},
        },
        expected: []Result{
            {Success: true},
            {Success: true, IsFollowing: true},
        },
    },
    {
        description: "follow and unfollow",
        operations: []Operation{
            {Type: "Follow", FollowerID: 1, FolloweeID: 2},
            {Type: "Unfollow", FollowerID: 1, FolloweeID: 2},
            {Type: "IsFollowing", FollowerID: 1, FolloweeID: 2},
        },
        expected: []Result{
            {Success: true},
            {Success: true},
            {Success: true, IsFollowing: false},
        },
    },
    {
        description: "get followers pagination",
        operations: []Operation{
            {Type: "Follow", FollowerID: 1, FolloweeID: 5},
            {Type: "Follow", FollowerID: 2, FolloweeID: 5},
            {Type: "Follow", FollowerID: 3, FolloweeID: 5},
            {Type: "GetFollowers", UserID: 5, Offset: 0, Limit: 2},
            {Type: "GetFollowers", UserID: 5, Offset: 2, Limit: 2},
        },
        expected: []Result{
            {Success: true},
            {Success: true},
            {Success: true},
            {Success: true, Users: []uint64{1, 2}},
            {Success: true, Users: []uint64{3}},
        },
    },
    {
        description: "get followees pagination",
        operations: []Operation{
            {Type: "Follow", FollowerID: 5, FolloweeID: 1},
            {Type: "Follow", FollowerID: 5, FolloweeID: 2},
            {Type: "Follow", FollowerID: 5, FolloweeID: 3},
            {Type: "GetFollowees", UserID: 5, Offset: 0, Limit: 2},
            {Type: "GetFollowees", UserID: 5, Offset: 2, Limit: 2},
        },
        expected: []Result{
            {Success: true},
            {Success: true},
            {Success: true},
            {Success: true, Users: []uint64{1, 2}},
            {Success: true, Users: []uint64{3}},
        },
    },
    {
        description: "mutual followees",
        operations: []Operation{
            {Type: "Follow", FollowerID: 1, FolloweeID: 10},
            {Type: "Follow", FollowerID: 1, FolloweeID: 11},
            {Type: "Follow", FollowerID: 1, FolloweeID: 12},
            {Type: "Follow", FollowerID: 2, FolloweeID: 10},
            {Type: "Follow", FollowerID: 2, FolloweeID: 11},
            {Type: "GetMutualFollowees", UserID: 1, OtherUserID: 2, Offset: 0, Limit: 3},
        },
        expected: []Result{
            {Success: true},
            {Success: true},
            {Success: true},
            {Success: true},
            {Success: true},
            {Success: true, Users: []uint64{10, 11}},
        },
    },
}