package network_cdn_test

import (
	"reflect"
	"testing"

	"network_cdn"
)

func TestBasicCase(t *testing.T) {
	servers := []int{1, 2, 3, 4}
	videos := []string{"video1.mp4", "video2.mp4"}
	storage := map[int][]string{
		1: {"video1.mp4"},
		2: {"video2.mp4", "video1.mp4"},
		3: {},
		4: {"video2.mp4"},
	}
	networkLinks := [][3]int{
		{1, 2, 10},
		{2, 3, 5},
		{1, 4, 20},
		{4, 3, 15},
	}
	requests := [][2]interface{}{
		{1, "video2.mp4"},
		{3, "video1.mp4"},
	}
	// Expected results:
	// For request {1, "video2.mp4"}: optimal server is 2 with cost 10.
	// For request {3, "video1.mp4"}: optimal server is 2 with cost 5 (path: 3->2).
	expected := [][2]int{
		{2, 10},
		{2, 5},
	}
	results := network_cdn.ServeVideos(servers, videos, storage, networkLinks, requests)
	if !reflect.DeepEqual(results, expected) {
		t.Errorf("TestBasicCase failed. Got: %v, expected: %v", results, expected)
	}
}

func TestNonexistentServerAndVideo(t *testing.T) {
	servers := []int{1, 2}
	videos := []string{"video1.mp4"}
	storage := map[int][]string{
		1: {"video1.mp4"},
		2: {},
	}
	networkLinks := [][3]int{
		{1, 2, 4},
	}
	requests := [][2]interface{}{
		{3, "video1.mp4"}, // User location does not exist.
		{1, "video2.mp4"}, // Requested video does not exist.
	}
	expected := [][2]int{
		{-1, -1},
		{-1, -1},
	}
	results := network_cdn.ServeVideos(servers, videos, storage, networkLinks, requests)
	if !reflect.DeepEqual(results, expected) {
		t.Errorf("TestNonexistentServerAndVideo failed. Got: %v, expected: %v", results, expected)
	}
}

func TestDisconnectedNetwork(t *testing.T) {
	// Two disconnected components.
	servers := []int{1, 2, 3, 4}
	videos := []string{"video1.mp4"}
	storage := map[int][]string{
		1: {"video1.mp4"},
		2: {},
		3: {"video1.mp4"},
		4: {},
	}
	networkLinks := [][3]int{
		{1, 2, 3}, // Component 1: servers 1-2.
		{3, 4, 2}, // Component 2: servers 3-4.
	}
	requests := [][2]interface{}{
		{2, "video1.mp4"}, // From component 1: best source is server 1 with cost 3.
		{4, "video1.mp4"}, // From component 2: best source is server 3 with cost 2.
		{2, "video1.mp4"}, // Repeated request from component 1.
	}
	expected := [][2]int{
		{1, 3},
		{3, 2},
		{1, 3},
	}
	results := network_cdn.ServeVideos(servers, videos, storage, networkLinks, requests)
	if !reflect.DeepEqual(results, expected) {
		t.Errorf("TestDisconnectedNetwork failed. Got: %v, expected: %v", results, expected)
	}
}

func TestParallelEdges(t *testing.T) {
	// Test when there are parallel edges with different costs.
	servers := []int{1, 2, 3}
	videos := []string{"video1.mp4"}
	storage := map[int][]string{
		1: {"video1.mp4"},
		2: {"video1.mp4"},
		3: {},
	}
	networkLinks := [][3]int{
		{3, 1, 10},
		{3, 1, 4}, // Parallel edge with lower cost.
		{3, 2, 6},
	}
	requests := [][2]interface{}{
		{3, "video1.mp4"},
	}
	// From server 3: optimal path is to server 1 with cost 4.
	expected := [][2]int{
		{1, 4},
	}
	results := network_cdn.ServeVideos(servers, videos, storage, networkLinks, requests)
	if !reflect.DeepEqual(results, expected) {
		t.Errorf("TestParallelEdges failed. Got: %v, expected: %v", results, expected)
	}
}

func TestTieBreaking(t *testing.T) {
	// When two servers offer the same minimal cost, the one with the smallest ID should be chosen.
	servers := []int{1, 2, 3}
	videos := []string{"video1.mp4"}
	storage := map[int][]string{
		1: {"video1.mp4"},
		2: {"video1.mp4"},
		3: {},
	}
	networkLinks := [][3]int{
		{3, 1, 5},
		{3, 2, 5},
	}
	requests := [][2]interface{}{
		{3, "video1.mp4"},
	}
	expected := [][2]int{
		{1, 5},
	}
	results := network_cdn.ServeVideos(servers, videos, storage, networkLinks, requests)
	if !reflect.DeepEqual(results, expected) {
		t.Errorf("TestTieBreaking failed. Got: %v, expected: %v", results, expected)
	}
}

func TestNoPath(t *testing.T) {
	// Test when there is no path between the user's server and any server storing the video.
	servers := []int{1, 2, 3}
	videos := []string{"video1.mp4"}
	storage := map[int][]string{
		1: {"video1.mp4"},
		2: {},
		3: {},
	}
	networkLinks := [][3]int{
		{2, 3, 7},
	}
	requests := [][2]interface{}{
		{3, "video1.mp4"}, // Server 3 is isolated from server 1.
	}
	expected := [][2]int{
		{-1, -1},
	}
	results := network_cdn.ServeVideos(servers, videos, storage, networkLinks, requests)
	if !reflect.DeepEqual(results, expected) {
		t.Errorf("TestNoPath failed. Got: %v, expected: %v", results, expected)
	}
}