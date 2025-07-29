package social_scale

import (
	"reflect"
	"sort"
	"sync"
	"testing"
)

// compareSlices checks if two string slices are equal (order-sensitive).
func compareSlices(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}

func TestAddAndRemoveUser(t *testing.T) {
	sg := NewSocialGraph()

	// Add users
	if err := sg.AddUser("alice"); err != nil {
		t.Fatalf("Failed to add user alice: %v", err)
	}
	if err := sg.AddUser("bob"); err != nil {
		t.Fatalf("Failed to add user bob: %v", err)
	}

	// Adding a duplicate user should return an error.
	if err := sg.AddUser("alice"); err == nil {
		t.Fatalf("Expected error when adding duplicate user alice")
	}

	// Remove an existing user.
	if err := sg.RemoveUser("bob"); err != nil {
		t.Fatalf("Failed to remove user bob: %v", err)
	}

	// Removing a non-existent user should error.
	if err := sg.RemoveUser("bob"); err == nil {
		t.Fatalf("Expected error when removing non-existent user bob")
	}
}

func TestFollowAndUnfollow(t *testing.T) {
	sg := NewSocialGraph()

	// Setup users.
	users := []string{"alice", "bob", "charlie"}
	for _, user := range users {
		if err := sg.AddUser(user); err != nil {
			t.Fatalf("Failed to add user %s: %v", user, err)
		}
	}

	// Valid follow operations.
	if err := sg.Follow("alice", "bob"); err != nil {
		t.Fatalf("alice failed to follow bob: %v", err)
	}
	if err := sg.Follow("bob", "alice"); err != nil {
		t.Fatalf("bob failed to follow alice: %v", err)
	}

	// A user cannot follow themselves.
	if err := sg.Follow("alice", "alice"); err == nil {
		t.Fatalf("Expected error when a user follows itself")
	}

	// Following a non-existent user should error.
	if err := sg.Follow("alice", "dave"); err == nil {
		t.Fatalf("Expected error when following a non-existent user")
	}

	// Test GetFollowing for alice.
	following, err := sg.GetFollowing("alice")
	if err != nil {
		t.Fatalf("Error getting following for alice: %v", err)
	}
	expectedFollowing := []string{"bob"}
	sort.Strings(following)
	if !reflect.DeepEqual(following, expectedFollowing) {
		t.Fatalf("Expected following for alice %v, got %v", expectedFollowing, following)
	}

	// Test GetFollowers for bob.
	followers, err := sg.GetFollowers("bob")
	if err != nil {
		t.Fatalf("Error getting followers for bob: %v", err)
	}
	expectedFollowers := []string{"alice"}
	sort.Strings(followers)
	if !reflect.DeepEqual(followers, expectedFollowers) {
		t.Fatalf("Expected followers for bob %v, got %v", expectedFollowers, followers)
	}

	// Unfollow operation.
	if err := sg.Unfollow("alice", "bob"); err != nil {
		t.Fatalf("Failed to unfollow: %v", err)
	}

	// Unfollowing a non-followed user should error.
	if err := sg.Unfollow("alice", "bob"); err == nil {
		t.Fatalf("Expected error when unfollowing a non-followed user")
	}
}

func TestMutualFollowers(t *testing.T) {
	sg := NewSocialGraph()
	users := []string{"alice", "bob", "charlie", "dave", "eve"}
	for _, user := range users {
		if err := sg.AddUser(user); err != nil {
			t.Fatalf("Failed to add user %s: %v", user, err)
		}
	}

	// Setup relationships:
	// alice follows dave and eve.
	if err := sg.Follow("alice", "dave"); err != nil {
		t.Fatalf("Error: %v", err)
	}
	if err := sg.Follow("alice", "eve"); err != nil {
		t.Fatalf("Error: %v", err)
	}

	// bob follows dave and eve.
	if err := sg.Follow("bob", "dave"); err != nil {
		t.Fatalf("Error: %v", err)
	}
	if err := sg.Follow("bob", "eve"); err != nil {
		t.Fatalf("Error: %v", err)
	}

	// charlie follows dave.
	if err := sg.Follow("charlie", "dave"); err != nil {
		t.Fatalf("Error: %v", err)
	}

	// Mutual followers of dave and eve should be alice and bob.
	mutual, err := sg.MutualFollowers("dave", "eve")
	if err != nil {
		t.Fatalf("Failed to get mutual followers: %v", err)
	}
	expected := []string{"alice", "bob"}
	sort.Strings(mutual)
	if !reflect.DeepEqual(mutual, expected) {
		t.Fatalf("Expected mutual followers %v, got %v", expected, mutual)
	}
}

func TestSuggestFriends(t *testing.T) {
	sg := NewSocialGraph()
	// Create a network of users.
	users := []string{"alice", "bob", "charlie", "dave", "eve", "frank", "grace"}
	for _, user := range users {
		if err := sg.AddUser(user); err != nil {
			t.Fatalf("Failed to add user %s: %v", user, err)
		}
	}

	// Build relationships:
	// alice follows bob and charlie.
	if err := sg.Follow("alice", "bob"); err != nil {
		t.Fatalf("Error: %v", err)
	}
	if err := sg.Follow("alice", "charlie"); err != nil {
		t.Fatalf("Error: %v", err)
	}

	// bob follows dave, eve, and grace.
	if err := sg.Follow("bob", "dave"); err != nil {
		t.Fatalf("Error: %v", err)
	}
	if err := sg.Follow("bob", "eve"); err != nil {
		t.Fatalf("Error: %v", err)
	}
	if err := sg.Follow("bob", "grace"); err != nil {
		t.Fatalf("Error: %v", err)
	}

	// charlie follows dave, frank, and grace.
	if err := sg.Follow("charlie", "dave"); err != nil {
		t.Fatalf("Error: %v", err)
	}
	if err := sg.Follow("charlie", "frank"); err != nil {
		t.Fatalf("Error: %v", err)
	}
	if err := sg.Follow("charlie", "grace"); err != nil {
		t.Fatalf("Error: %v", err)
	}

	// For alice:
	// bob's following: [dave, eve, grace]
	// charlie's following: [dave, frank, grace]
	// Aggregate potential candidates: dave (2), grace (2), eve (1), frank (1)
	// When K=2, only dave and grace should be returned.
	suggestions, err := sg.SuggestFriends("alice", 2, 10)
	if err != nil {
		t.Fatalf("Failed to get friend suggestions for alice: %v", err)
	}
	expected := []string{"dave", "grace"}
	if !compareSlices(suggestions, expected) {
		t.Fatalf("Expected suggestions %v, got %v", expected, suggestions)
	}

	// When K=1 and N=1, only the lexicographically smallest candidate should be returned.
	suggestions2, err := sg.SuggestFriends("alice", 1, 1)
	if err != nil {
		t.Fatalf("Failed to get friend suggestions for alice with K=1, N=1: %v", err)
	}
	expected2 := []string{"dave"}
	if !compareSlices(suggestions2, expected2) {
		t.Fatalf("Expected suggestions %v, got %v", expected2, suggestions2)
	}
}

func TestConcurrentOperations(t *testing.T) {
	sg := NewSocialGraph()
	users := []string{"alice", "bob", "charlie", "dave", "eve", "frank", "grace"}
	for _, user := range users {
		if err := sg.AddUser(user); err != nil {
			t.Fatalf("Failed to add user %s: %v", user, err)
		}
	}

	var wg sync.WaitGroup
	ops := []func(){
		func() { _ = sg.Follow("alice", "bob") },
		func() { _ = sg.Follow("bob", "charlie") },
		func() { _ = sg.Follow("charlie", "dave") },
		func() { _ = sg.Follow("dave", "eve") },
		func() { _ = sg.Follow("eve", "frank") },
		func() { _ = sg.Follow("frank", "grace") },
	}

	// Execute operations concurrently.
	for _, op := range ops {
		wg.Add(1)
		go func(opFunc func()) {
			defer wg.Done()
			opFunc()
		}(op)
	}
	wg.Wait()

	// Validate one of the relationships.
	followersBob, err := sg.GetFollowers("bob")
	if err != nil {
		t.Fatalf("Failed to get followers for bob: %v", err)
	}
	expectedFollowersBob := []string{"alice"}
	sort.Strings(followersBob)
	if !reflect.DeepEqual(followersBob, expectedFollowersBob) {
		t.Fatalf("Expected bob's followers to be %v, got %v", expectedFollowersBob, followersBob)
	}
}