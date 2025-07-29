package social_network

import "testing"

func BenchmarkSocialNetwork(b *testing.B) {
	sn := NewSocialNetwork()
	
	// Setup: Add 1000 users and connect them in a grid pattern
	for i := 0; i < 1000; i++ {
		sn.AddUser(i)
		if i > 0 {
			sn.Connect(i-1, i)
		}
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		// Test various operations
		sn.GetFriends(500)
		sn.GetMutualFriends(100, 900)
		sn.GetShortestFriendshipPath(0, 999)
	}
}