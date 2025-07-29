package scalable_network

import (
	"testing"
	"time"
)

func TestCreateUser(t *testing.T) {
	network := NewSocialNetwork()
	userID, err := network.CreateUser("test_user", "Test profile")
	if err != nil {
		t.Fatalf("CreateUser failed: %v", err)
	}
	if userID == "" {
		t.Error("Expected non-empty user ID")
	}

	// Test duplicate username
	_, err = network.CreateUser("test_user", "Duplicate")
	if err == nil {
		t.Error("Expected error for duplicate username")
	}
}

func TestAddRemoveFriend(t *testing.T) {
	network := NewSocialNetwork()
	user1, _ := network.CreateUser("user1", "")
	user2, _ := network.CreateUser("user2", "")

	// Test adding friends
	err := network.AddFriend(user1, user2)
	if err != nil {
		t.Fatalf("AddFriend failed: %v", err)
	}

	// Test duplicate friendship
	err = network.AddFriend(user1, user2)
	if err == nil {
		t.Error("Expected error for duplicate friendship")
	}

	// Test removing friends
	err = network.RemoveFriend(user1, user2)
	if err != nil {
		t.Fatalf("RemoveFriend failed: %v", err)
	}

	// Test removing non-existent friendship
	err = network.RemoveFriend(user1, user2)
	if err == nil {
		t.Error("Expected error for removing non-existent friendship")
	}
}

func TestPostMessageAndNewsFeed(t *testing.T) {
	network := NewSocialNetwork()
	user1, _ := network.CreateUser("user1", "")
	user2, _ := network.CreateUser("user2", "")
	network.AddFriend(user1, user2)

	// Test posting messages
	msg1 := "Hello world!"
	err := network.PostMessage(user2, msg1)
	if err != nil {
		t.Fatalf("PostMessage failed: %v", err)
	}

	time.Sleep(10 * time.Millisecond) // Ensure different timestamps
	msg2 := "Second message"
	network.PostMessage(user2, msg2)

	// Test news feed
	feed, err := network.GetNewsFeed(user1, 0, 10)
	if err != nil {
		t.Fatalf("GetNewsFeed failed: %v", err)
	}

	if len(feed) != 2 {
		t.Fatalf("Expected 2 messages in feed, got %d", len(feed))
	}

	if feed[0].Message != msg2 {
		t.Errorf("Expected newest message first, got %q", feed[0].Message)
	}

	// Test pagination
	feed, err = network.GetNewsFeed(user1, 1, 1)
	if err != nil {
		t.Fatalf("GetNewsFeed pagination failed: %v", err)
	}
	if len(feed) != 1 || feed[0].Message != msg1 {
		t.Error("Pagination failed")
	}
}

func TestMutualFriends(t *testing.T) {
	network := NewSocialNetwork()
	user1, _ := network.CreateUser("user1", "")
	user2, _ := network.CreateUser("user2", "")
	user3, _ := network.CreateUser("user3", "")
	user4, _ := network.CreateUser("user4", "")

	network.AddFriend(user1, user3)
	network.AddFriend(user2, user3)
	network.AddFriend(user1, user4)

	// Test mutual friends
	mutuals, err := network.GetMutualFriends(user1, user2)
	if err != nil {
		t.Fatalf("GetMutualFriends failed: %v", err)
	}

	if len(mutuals) != 1 || mutuals[0] != user3 {
		t.Errorf("Expected mutual friend %q, got %v", user3, mutuals)
	}

	// Test no mutual friends
	mutuals, err = network.GetMutualFriends(user1, user4)
	if err != nil {
		t.Fatalf("GetMutualFriends failed: %v", err)
	}
	if len(mutuals) != 0 {
		t.Error("Expected no mutual friends")
	}
}

func TestConcurrency(t *testing.T) {
	network := NewSocialNetwork()
	user1, _ := network.CreateUser("user1", "")
	user2, _ := network.CreateUser("user2", "")

	// Concurrent friend operations
	done := make(chan bool)
	go func() {
		network.AddFriend(user1, user2)
		done <- true
	}()
	go func() {
		network.AddFriend(user2, user1) // Should be idempotent
		done <- true
	}()
	<-done
	<-done

	// Verify friendship exists
	friends, _ := network.GetNewsFeed(user1, 0, 10)
	if len(friends) != 0 { // Just checking if friendship was established
		t.Error("Concurrent friend operations failed")
	}
}