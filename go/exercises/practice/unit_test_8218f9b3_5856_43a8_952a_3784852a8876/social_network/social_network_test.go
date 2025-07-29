package social_network

import (
	"reflect"
	"sync"
	"testing"
)

func TestAddUser(t *testing.T) {
	t.Run("add single user", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		if friends := sn.GetFriends(1); len(friends) != 0 {
			t.Errorf("Expected no friends for new user, got %v", friends)
		}
	})

	t.Run("add duplicate user", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.AddUser(1)
		if friends := sn.GetFriends(1); len(friends) != 0 {
			t.Errorf("Expected no friends for duplicate user, got %v", friends)
		}
	})
}

func TestRemoveUser(t *testing.T) {
	t.Run("remove existing user", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.RemoveUser(1)
		if friends := sn.GetFriends(1); len(friends) != 0 {
			t.Errorf("Expected user to be removed, got %v", friends)
		}
	})

	t.Run("remove non-existent user", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.RemoveUser(999)
		// Should not panic or error
	})
}

func TestConnect(t *testing.T) {
	t.Run("connect two users", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.AddUser(2)
		sn.Connect(1, 2)
		if !reflect.DeepEqual(sn.GetFriends(1), []int{2}) {
			t.Errorf("Expected user 1 to have friend 2")
		}
		if !reflect.DeepEqual(sn.GetFriends(2), []int{1}) {
			t.Errorf("Expected user 2 to have friend 1")
		}
	})

	t.Run("connect non-existent users", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.Connect(1, 2) // Should not panic
	})
}

func TestDisconnect(t *testing.T) {
	t.Run("disconnect connected users", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.AddUser(2)
		sn.Connect(1, 2)
		sn.Disconnect(1, 2)
		if len(sn.GetFriends(1)) != 0 || len(sn.GetFriends(2)) != 0 {
			t.Errorf("Expected users to be disconnected")
		}
	})

	t.Run("disconnect non-connected users", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.AddUser(2)
		sn.Disconnect(1, 2) // Should not panic
	})
}

func TestGetMutualFriends(t *testing.T) {
	t.Run("no mutual friends", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.AddUser(2)
		if mutual := sn.GetMutualFriends(1, 2); len(mutual) != 0 {
			t.Errorf("Expected no mutual friends, got %v", mutual)
		}
	})

	t.Run("with mutual friends", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.AddUser(2)
		sn.AddUser(3)
		sn.Connect(1, 3)
		sn.Connect(2, 3)
		if !reflect.DeepEqual(sn.GetMutualFriends(1, 2), []int{3}) {
			t.Errorf("Expected mutual friend 3")
		}
	})
}

func TestGetShortestFriendshipPath(t *testing.T) {
	t.Run("direct connection", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.AddUser(2)
		sn.Connect(1, 2)
		if !reflect.DeepEqual(sn.GetShortestFriendshipPath(1, 2), []int{1, 2}) {
			t.Errorf("Expected direct path [1,2]")
		}
	})

	t.Run("multi-hop path", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.AddUser(2)
		sn.AddUser(3)
		sn.Connect(1, 2)
		sn.Connect(2, 3)
		if !reflect.DeepEqual(sn.GetShortestFriendshipPath(1, 3), []int{1, 2, 3}) {
			t.Errorf("Expected path [1,2,3]")
		}
	})

	t.Run("no path exists", func(t *testing.T) {
		sn := NewSocialNetwork()
		sn.AddUser(1)
		sn.AddUser(2)
		if path := sn.GetShortestFriendshipPath(1, 2); len(path) != 0 {
			t.Errorf("Expected no path, got %v", path)
		}
	})
}

func TestConcurrentAccess(t *testing.T) {
	sn := NewSocialNetwork()
	var wg sync.WaitGroup

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			sn.AddUser(id)
			sn.AddUser(id + 1000)
			sn.Connect(id, id+1000)
			sn.GetFriends(id)
			sn.GetMutualFriends(id, id+1000)
		}(i)
	}

	wg.Wait()

	// Verify all connections were made properly
	for i := 0; i < 100; i++ {
		if !reflect.DeepEqual(sn.GetFriends(i), []int{i + 1000}) {
			t.Errorf("Concurrent test failed for user %d", i)
		}
	}
}