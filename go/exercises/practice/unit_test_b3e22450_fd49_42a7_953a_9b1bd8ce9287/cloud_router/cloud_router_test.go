package cloud_router

import (
	"testing"
	"time"
)

func TestAddAndRoutePacket(t *testing.T) {
	router := NewRouterSystem()

	// Test basic rule addition and routing
	router.AddRule("router1", "rule1", map[string]string{"color": "red"}, "router2")
	router.AddRule("router1", "rule2", map[string]string{"color": "blue"}, "router3")
	router.AddRule("router1", "rule3", map[string]string{}, "router4") // Default route

	// Test exact match
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red"}); target != "router2" {
		t.Errorf("Expected router2, got %s", target)
	}

	// Test another exact match
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "blue"}); target != "router3" {
		t.Errorf("Expected router3, got %s", target)
	}

	// Test default route
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"shape": "circle"}); target != "router4" {
		t.Errorf("Expected router4, got %s", target)
	}

	// Test no match (should return empty string)
	if target := router.RoutePacket("router2", "1.2.3.4", map[string]string{"color": "green"}); target != "" {
		t.Errorf("Expected empty string, got %s", target)
	}
}

func TestRulePriority(t *testing.T) {
	router := NewRouterSystem()

	// Add rules with different priority levels
	router.AddRule("router1", "rule1", map[string]string{"color": "red"}, "router2")
	router.AddRule("router1", "rule2", map[string]string{"color": "red", "size": "large"}, "router3")
	router.AddRule("router1", "rule3", map[string]string{"color": "red", "size": "large", "shape": "circle"}, "router4")

	// Test that more specific rule takes priority
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red", "size": "large", "shape": "circle"}); target != "router4" {
		t.Errorf("Expected router4, got %s", target)
	}

	// Test with fewer attributes
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red", "size": "large"}); target != "router3" {
		t.Errorf("Expected router3, got %s", target)
	}

	// Test with single attribute
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red"}); target != "router2" {
		t.Errorf("Expected router2, got %s", target)
	}
}

func TestRemoveRule(t *testing.T) {
	router := NewRouterSystem()

	router.AddRule("router1", "rule1", map[string]string{"color": "red"}, "router2")
	router.AddRule("router1", "rule2", map[string]string{"color": "blue"}, "router3")

	// Test routing before removal
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red"}); target != "router2" {
		t.Errorf("Expected router2, got %s", target)
	}

	// Remove rule
	router.RemoveRule("router1", "rule1")

	// Test routing after removal
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red"}); target != "" {
		t.Errorf("Expected empty string, got %s", target)
	}

	// Other rules should still work
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "blue"}); target != "router3" {
		t.Errorf("Expected router3, got %s", target)
	}
}

func TestConcurrentAccess(t *testing.T) {
	router := NewRouterSystem()

	// Add initial rule
	router.AddRule("router1", "rule1", map[string]string{"color": "red"}, "router2")

	// Start goroutines to simulate concurrent access
	done := make(chan bool)
	for i := 0; i < 10; i++ {
		go func() {
			for j := 0; j < 100; j++ {
				router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red"})
			}
			done <- true
		}()
	}

	// Add more rules while routing is happening
	go func() {
		for i := 0; i < 5; i++ {
			router.AddRule("router1", "rule_new"+string(rune(i)), map[string]string{"color": "blue"}, "router3")
			time.Sleep(10 * time.Millisecond)
		}
		done <- true
	}()

	// Wait for all goroutines to finish
	for i := 0; i < 11; i++ {
		<-done
	}

	// Final check to ensure system is in consistent state
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red"}); target != "router2" {
		t.Errorf("Expected router2, got %s", target)
	}
}

func TestMultipleRouters(t *testing.T) {
	router := NewRouterSystem()

	// Add rules to different routers
	router.AddRule("router1", "rule1", map[string]string{"color": "red"}, "router2")
	router.AddRule("router2", "rule2", map[string]string{"color": "blue"}, "router3")

	// Test routing through different routers
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "red"}); target != "router2" {
		t.Errorf("Expected router2, got %s", target)
	}

	if target := router.RoutePacket("router2", "1.2.3.4", map[string]string{"color": "blue"}); target != "router3" {
		t.Errorf("Expected router3, got %s", target)
	}

	// Test that rules don't leak between routers
	if target := router.RoutePacket("router1", "1.2.3.4", map[string]string{"color": "blue"}); target != "" {
		t.Errorf("Expected empty string, got %s", target)
	}
}