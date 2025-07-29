package socialfeed

import (
	"reflect"
	"testing"
)

func TestSocialFeed(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			feed := NewSocialFeed()
			
			// Execute all operations
			for _, op := range tc.operations {
				switch op.opType {
				case "addUser":
					err := feed.AddUser(op.userID)
					if err != nil {
						t.Fatalf("Failed to add user %d: %v", op.userID, err)
					}
				case "addFollower":
					err := feed.AddFollower(op.userID, op.targetID)
					if err != nil {
						t.Fatalf("Failed to add follower relationship %d->%d: %v", 
							op.userID, op.targetID, err)
					}
				case "createPost":
					err := feed.CreatePost(op.userID, op.content, op.timestamp, op.likes)
					if err != nil {
						t.Fatalf("Failed to create post for user %d: %v", op.userID, err)
					}
				}
			}

			// Get feed for user 1 (the test user) with offset 0 and limit 10
			result, err := feed.GetUserFeed(1, 0, 10)
			if err != nil {
				t.Fatalf("Failed to get user feed: %v", err)
			}

			// Compare results
			if !reflect.DeepEqual(result, tc.expected) {
				t.Errorf("GetUserFeed() = %v, want %v", result, tc.expected)
			}
		})
	}
}

func BenchmarkSocialFeed(b *testing.B) {
	feed := NewSocialFeed()
	
	// Setup: Create some users and relationships
	userIDs := []int64{1, 2, 3, 4, 5}
	for _, id := range userIDs {
		feed.AddUser(id)
	}
	
	// User 1 follows all other users
	for i := 2; i <= 5; i++ {
		feed.AddFollower(1, int64(i))
	}

	// Create some initial posts
	for i := 2; i <= 5; i++ {
		feed.CreatePost(int64(i), "Benchmark post", int64(i*1000), int64(i))
	}

	b.ResetTimer()
	
	for i := 0; i < b.N; i++ {
		// Benchmark feed retrieval
		_, err := feed.GetUserFeed(1, 0, 10)
		if err != nil {
			b.Fatalf("Failed to get user feed: %v", err)
		}
	}
}