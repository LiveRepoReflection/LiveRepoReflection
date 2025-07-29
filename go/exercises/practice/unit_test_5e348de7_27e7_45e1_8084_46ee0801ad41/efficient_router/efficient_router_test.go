package efficient_router

import (
	"fmt"
	"math/rand"
	"testing"
	"time"
)

func TestBuildRoutingTable(t *testing.T) {
	router := NewRouter()
	
	rules := []Rule{
		{Prefix: "192.168.1.0/24", NextHop: "RouterA", Metric: 10},
		{Prefix: "192.168.0.0/16", NextHop: "RouterB", Metric: 20},
		{Prefix: "0.0.0.0/0", NextHop: "RouterC", Metric: 30},
	}
	
	err := router.BuildRoutingTable(rules)
	if err != nil {
		t.Errorf("BuildRoutingTable() error = %v, want nil", err)
	}
}

func TestBuildRoutingTableInvalidInput(t *testing.T) {
	router := NewRouter()
	
	// Test with invalid CIDR notation
	invalidRules := []Rule{
		{Prefix: "not-an-ip-address", NextHop: "RouterA", Metric: 10},
	}
	
	err := router.BuildRoutingTable(invalidRules)
	if err == nil {
		t.Error("BuildRoutingTable() with invalid IP format did not return an error")
	}
	
	// Test with invalid prefix length
	invalidRules = []Rule{
		{Prefix: "192.168.1.0/40", NextHop: "RouterA", Metric: 10}, // IPv4 prefix length can't be > 32
	}
	
	err = router.BuildRoutingTable(invalidRules)
	if err == nil {
		t.Error("BuildRoutingTable() with invalid prefix length did not return an error")
	}
}

func TestRouteIP(t *testing.T) {
	for _, tc := range routingRuleTests {
		t.Run(tc.description, func(t *testing.T) {
			router := NewRouter()
			err := router.BuildRoutingTable(tc.routingRules)
			if err != nil {
				t.Fatalf("BuildRoutingTable() error = %v", err)
			}
			
			for i, ip := range tc.ipAddresses {
				nextHop, err := router.RouteIP(ip)
				if err != nil {
					t.Errorf("RouteIP(%s) error = %v", ip, err)
				}
				if nextHop != tc.expectedNextHops[i] {
					t.Errorf("RouteIP(%s) = %s, want %s", ip, nextHop, tc.expectedNextHops[i])
				}
			}
		})
	}
}

func TestRouteIPInvalidInput(t *testing.T) {
	router := NewRouter()
	rules := []Rule{
		{Prefix: "192.168.1.0/24", NextHop: "RouterA", Metric: 10},
	}
	
	err := router.BuildRoutingTable(rules)
	if err != nil {
		t.Fatalf("BuildRoutingTable() error = %v", err)
	}
	
	_, err = router.RouteIP("not-an-ip-address")
	if err == nil {
		t.Error("RouteIP() with invalid IP did not return an error")
	}
}

func TestRouteIPStream(t *testing.T) {
	for _, tc := range routingRuleTests {
		t.Run(tc.description, func(t *testing.T) {
			router := NewRouter()
			err := router.BuildRoutingTable(tc.routingRules)
			if err != nil {
				t.Fatalf("BuildRoutingTable() error = %v", err)
			}
			
			results, err := router.RouteIPStream(tc.ipAddresses)
			if err != nil {
				t.Errorf("RouteIPStream() error = %v", err)
			}
			
			if len(results) != len(tc.expectedNextHops) {
				t.Errorf("RouteIPStream() returned %d results, want %d", len(results), len(tc.expectedNextHops))
			}
			
			for i, result := range results {
				if result != tc.expectedNextHops[i] {
					t.Errorf("RouteIPStream() result[%d] = %s, want %s", i, result, tc.expectedNextHops[i])
				}
			}
		})
	}
}

// Helper function to generate random IP address
func randomIP() string {
	return fmt.Sprintf("%d.%d.%d.%d", 
		rand.Intn(256), 
		rand.Intn(256), 
		rand.Intn(256), 
		rand.Intn(256))
}

// Helper function to generate random CIDR prefix
func randomCIDR() string {
	return fmt.Sprintf("%d.%d.%d.%d/%d", 
		rand.Intn(256), 
		rand.Intn(256), 
		rand.Intn(256), 
		rand.Intn(256),
		rand.Intn(33)) // IPv4 prefix length 0-32
}

func TestPerformanceWithLargeRoutingTables(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping performance test in short mode")
	}

	rand.Seed(time.Now().UnixNano())
	
	for _, tc := range largeRoutingTableTests {
		t.Run(tc.description, func(t *testing.T) {
			// Generate random rules
			rules := make([]Rule, tc.routingRuleCount)
			for i := 0; i < tc.routingRuleCount; i++ {
				rules[i] = Rule{
					Prefix:  randomCIDR(),
					NextHop: fmt.Sprintf("Router%d", i),
					Metric:  rand.Intn(100),
				}
			}
			
			// Add a default route to ensure at least one route always matches
			rules = append(rules, Rule{
				Prefix:  "0.0.0.0/0",
				NextHop: "DefaultRouter",
				Metric:  100,
			})
			
			// Generate random IP addresses
			ipAddresses := make([]string, tc.ipAddressCount)
			for i := 0; i < tc.ipAddressCount; i++ {
				ipAddresses[i] = randomIP()
			}
			
			// Measure time to build the routing table
			startTime := time.Now()
			router := NewRouter()
			err := router.BuildRoutingTable(rules)
			if err != nil {
				t.Fatalf("BuildRoutingTable() error = %v", err)
			}
			buildTime := time.Since(startTime)
			
			// Measure time to route all IP addresses
			startTime = time.Now()
			_, err = router.RouteIPStream(ipAddresses)
			if err != nil {
				t.Fatalf("RouteIPStream() error = %v", err)
			}
			routeTime := time.Since(startTime)
			
			t.Logf("Build time: %v for %d rules", buildTime, tc.routingRuleCount)
			t.Logf("Route time: %v for %d IPs", routeTime, tc.ipAddressCount)
			t.Logf("Average route time per IP: %v", routeTime/time.Duration(tc.ipAddressCount))
		})
	}
}

func BenchmarkBuildRoutingTable(b *testing.B) {
	rand.Seed(time.Now().UnixNano())
	
	// Generate 1000 random rules for benchmarking
	rules := make([]Rule, 1000)
	for i := 0; i < 1000; i++ {
		rules[i] = Rule{
			Prefix:  randomCIDR(),
			NextHop: fmt.Sprintf("Router%d", i),
			Metric:  rand.Intn(100),
		}
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		router := NewRouter()
		err := router.BuildRoutingTable(rules)
		if err != nil {
			b.Fatalf("BuildRoutingTable() error = %v", err)
		}
	}
}

func BenchmarkRouteIP(b *testing.B) {
	rand.Seed(time.Now().UnixNano())
	
	// Generate 1000 random rules
	rules := make([]Rule, 1000)
	for i := 0; i < 1000; i++ {
		rules[i] = Rule{
			Prefix:  randomCIDR(),
			NextHop: fmt.Sprintf("Router%d", i),
			Metric:  rand.Intn(100),
		}
	}
	
	// Add a default route
	rules = append(rules, Rule{
		Prefix:  "0.0.0.0/0",
		NextHop: "DefaultRouter",
		Metric:  100,
	})
	
	// Generate 100 random IPs for benchmarking
	ipAddresses := make([]string, 100)
	for i := 0; i < 100; i++ {
		ipAddresses[i] = randomIP()
	}
	
	// Build the routing table
	router := NewRouter()
	err := router.BuildRoutingTable(rules)
	if err != nil {
		b.Fatalf("BuildRoutingTable() error = %v", err)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		// Route a random IP from our set
		ip := ipAddresses[i%len(ipAddresses)]
		_, err := router.RouteIP(ip)
		if err != nil {
			b.Fatalf("RouteIP(%s) error = %v", ip, err)
		}
	}
}