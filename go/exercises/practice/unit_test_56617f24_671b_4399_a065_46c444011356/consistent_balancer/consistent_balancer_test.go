package consistent_balancer_test

import (
	"errors"
	"strconv"
	"sync"
	"testing"
	"time"

	"consistent_balancer"
)

const totalKeys = 10000

func TestRegisterAndGetStatus(t *testing.T) {
	bal := consistent_balancer.NewBalancer(100) // 100 virtual nodes per server for better distribution

	serverID := "server-1"
	bal.RegisterServer(serverID)

	status := bal.GetServerStatus(serverID)
	if status != "online" {
		t.Errorf("Expected server %s to be online, got: %s", serverID, status)
	}

	// Register another server and verify its status
	serverID2 := "server-2"
	bal.RegisterServer(serverID2)
	status2 := bal.GetServerStatus(serverID2)
	if status2 != "online" {
		t.Errorf("Expected server %s to be online, got: %s", serverID2, status2)
	}
}

func TestMappingConsistency(t *testing.T) {
	bal := consistent_balancer.NewBalancer(100)
	// Register multiple servers
	servers := []string{"server-1", "server-2", "server-3", "server-4", "server-5"}
	for _, s := range servers {
		bal.RegisterServer(s)
	}

	// Save initial mapping for a set of keys
	keys := []string{"keyA", "keyB", "keyC", "keyD", "keyE", "keyF"}
	initialMapping := make(map[string]string)
	for _, k := range keys {
		initialMapping[k] = bal.GetServerForKey(k)
	}

	// Add an additional server and verify that most keys still map to the same server
	bal.RegisterServer("server-6")
	sameCount := 0
	for _, k := range keys {
		newMapping := bal.GetServerForKey(k)
		if newMapping == initialMapping[k] {
			sameCount++
		}
	}
	if sameCount < len(keys)/2 {
		t.Errorf("Mapping changed for too many keys after adding a server: %d out of %d keys retained their mapping", sameCount, len(keys))
	}

	// Remove a server and ensure none of the keys map to the removed server
	bal.UnregisterServer("server-3")
	for _, k := range keys {
		mappedServer := bal.GetServerForKey(k)
		if mappedServer == "server-3" {
			t.Errorf("After unregistering, key %s still maps to removed server server-3", k)
		}
	}
}

func TestUniformDistribution(t *testing.T) {
	bal := consistent_balancer.NewBalancer(200)
	// Register a larger set of servers
	servers := []string{"server-1", "server-2", "server-3", "server-4", "server-5", "server-6", "server-7", "server-8"}
	for _, s := range servers {
		bal.RegisterServer(s)
	}

	distribution := make(map[string]int)
	for i := 0; i < totalKeys; i++ {
		key := "key-" + strconv.Itoa(i)
		server := bal.GetServerForKey(key)
		distribution[server]++
	}

	// Evaluate the distribution across servers
	var min, max int
	min = totalKeys
	max = 0
	for _, count := range distribution {
		if count < min {
			min = count
		}
		if count > max {
			max = count
		}
	}

	if float64(max-min) > float64(totalKeys)/10.0 {
		t.Errorf("Distribution variance too high: min = %d, max = %d", min, max)
	}
}

func TestConcurrency(t *testing.T) {
	bal := consistent_balancer.NewBalancer(100)
	servers := []string{"server-1", "server-2", "server-3", "server-4"}
	var wg sync.WaitGroup

	// Concurrent server registration
	for _, s := range servers {
		wg.Add(1)
		go func(server string) {
			defer wg.Done()
			bal.RegisterServer(server)
		}(s)
	}
	wg.Wait()

	// Concurrent key mapping operations
	wg = sync.WaitGroup{}
	keys := make([]string, totalKeys)
	for i := 0; i < totalKeys; i++ {
		keys[i] = "key-" + strconv.Itoa(i)
	}

	errorCh := make(chan error, 100)
	for _, key := range keys {
		wg.Add(1)
		go func(k string) {
			defer wg.Done()
			server := bal.GetServerForKey(k)
			if server == "" {
				errorCh <- errors.New("mapped server is empty for key: " + k)
			}
		}(key)
	}
	wg.Wait()
	close(errorCh)
	for err := range errorCh {
		t.Error(err)
	}

	// Concurrent registration and unregistration operations
	wg = sync.WaitGroup{}
	for i := 5; i < 15; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			id := "server-" + strconv.Itoa(idx)
			bal.RegisterServer(id)
			time.Sleep(10 * time.Millisecond)
			bal.UnregisterServer(id)
		}(i)
	}
	wg.Wait()
}