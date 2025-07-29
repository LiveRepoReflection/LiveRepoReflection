package social_recommender

import (
	"testing"
	"reflect"
)

func TestAddUser(t *testing.T) {
	sg := NewSocialGraph()
	sg.AddUser("user1", []string{"go", "hiking"})
	sg.AddUser("user2", []string{"python", "swimming"})

	if sg.GetSize() != 2 {
		t.Errorf("Expected size 2, got %d", sg.GetSize())
	}
}

func TestRemoveUser(t *testing.T) {
	sg := NewSocialGraph()
	sg.AddUser("user1", []string{"go"})
	sg.AddUser("user2", []string{"python"})
	sg.RemoveUser("user1")

	if sg.GetSize() != 1 {
		t.Errorf("Expected size 1 after removal, got %d", sg.GetSize())
	}
}

func TestConnectAndDisconnect(t *testing.T) {
	sg := NewSocialGraph()
	sg.AddUser("user1", []string{"go"})
	sg.AddUser("user2", []string{"python"})
	sg.Connect("user1", "user2")

	if !sg.IsConnected("user1", "user2") {
		t.Error("Expected user1 to be connected to user2")
	}

	sg.Disconnect("user1", "user2")
	if sg.IsConnected("user1", "user2") {
		t.Error("Expected connection to be removed")
	}
}

func TestGetRecommendations(t *testing.T) {
	sg := NewSocialGraph()
	sg.AddUser("user1", []string{"go", "hiking"})
	sg.AddUser("user2", []string{"go", "swimming"})
	sg.AddUser("user3", []string{"python", "hiking"})
	sg.AddUser("user4", []string{"go", "hiking", "swimming"})
	sg.AddUser("user5", []string{"java", "cycling"})

	sg.Connect("user1", "user2")
	sg.Connect("user2", "user3")
	sg.Connect("user3", "user4")

	recommendations := sg.GetRecommendations("user1", 2)
	expected := []string{"user4", "user3"}

	if !reflect.DeepEqual(recommendations, expected) {
		t.Errorf("Expected recommendations %v, got %v", expected, recommendations)
	}
}

func TestGetRecommendationsWithMax(t *testing.T) {
	sg := NewSocialGraph()
	sg.AddUser("user1", []string{"go"})
	sg.AddUser("user2", []string{"go"})
	sg.AddUser("user3", []string{"go"})
	sg.AddUser("user4", []string{"go"})

	recommendations := sg.GetRecommendations("user1", 2)
	if len(recommendations) > 2 {
		t.Errorf("Expected max 2 recommendations, got %d", len(recommendations))
	}
}

func TestGetRecommendationsNoDuplicates(t *testing.T) {
	sg := NewSocialGraph()
	sg.AddUser("user1", []string{"go"})
	sg.AddUser("user2", []string{"go"})
	sg.AddUser("user3", []string{"go"})

	sg.Connect("user1", "user2")
	sg.Connect("user2", "user3")
	sg.Connect("user1", "user3")

	recommendations := sg.GetRecommendations("user1", 5)
	seen := make(map[string]bool)
	for _, rec := range recommendations {
		if seen[rec] {
			t.Errorf("Duplicate recommendation found: %s", rec)
		}
		seen[rec] = true
	}
}

func TestGetRecommendationsNoExistingConnections(t *testing.T) {
	sg := NewSocialGraph()
	sg.AddUser("user1", []string{"go"})
	sg.AddUser("user2", []string{"go"})
	sg.Connect("user1", "user2")

	recommendations := sg.GetRecommendations("user1", 1)
	if len(recommendations) != 0 {
		t.Errorf("Expected no recommendations when all users are connected, got %v", recommendations)
	}
}

func TestConcurrentAccess(t *testing.T) {
	sg := NewSocialGraph()
	done := make(chan bool)

	go func() {
		sg.AddUser("user1", []string{"go"})
		done <- true
	}()
	go func() {
		sg.AddUser("user2", []string{"python"})
		done <- true
	}()

	<-done
	<-done

	if sg.GetSize() != 2 {
		t.Errorf("Expected size 2 after concurrent adds, got %d", sg.GetSize())
	}
}