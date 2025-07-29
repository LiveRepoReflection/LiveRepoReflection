package service_router

import (
	"testing"
	"time"
)

func TestServiceRegistry(t *testing.T) {
	t.Run("Register and Get instances", func(t *testing.T) {
		registry := NewServiceRegistry()
		instance1 := ServiceInstance{
			ServiceName: "payment",
			InstanceID:  "instance1",
			Status:      Healthy,
			Metadata:    map[string]string{"version": "v1", "region": "us-east"},
			Weight:      10,
		}
		instance2 := ServiceInstance{
			ServiceName: "payment",
			InstanceID:  "instance2",
			Status:      Degraded,
			Metadata:    map[string]string{"version": "v2", "region": "us-west"},
			Weight:      5,
		}

		registry.RegisterOrUpdate(instance1)
		registry.RegisterOrUpdate(instance2)

		instances := registry.GetInstances("payment")
		if len(instances) != 2 {
			t.Fatalf("Expected 2 instances, got %d", len(instances))
		}
	})

	t.Run("Remove instance", func(t *testing.T) {
		registry := NewServiceRegistry()
		instance := ServiceInstance{
			ServiceName: "inventory",
			InstanceID:  "instance1",
			Status:      Healthy,
		}

		registry.RegisterOrUpdate(instance)
		registry.Remove("inventory", "instance1")

		instances := registry.GetInstances("inventory")
		if len(instances) != 0 {
			t.Fatalf("Expected 0 instances after removal, got %d", len(instances))
		}
	})

	t.Run("Concurrent access", func(t *testing.T) {
		registry := NewServiceRegistry()
		done := make(chan bool)

		go func() {
			for i := 0; i < 1000; i++ {
				instance := ServiceInstance{
					ServiceName: "cart",
					InstanceID:  "instance1",
					Status:      Healthy,
				}
				registry.RegisterOrUpdate(instance)
			}
			done <- true
		}()

		go func() {
			for i := 0; i < 1000; i++ {
				registry.GetInstances("cart")
			}
			done <- true
		}()

		<-done
		<-done
	})
}

func TestRoutingEngine(t *testing.T) {
	registry := NewServiceRegistry()
	router := NewRouter(registry)

	healthyInstance := ServiceInstance{
		ServiceName: "search",
		InstanceID:  "healthy1",
		Status:      Healthy,
		Metadata:    map[string]string{"version": "v1", "env": "prod"},
		Weight:      10,
	}
	degradedInstance := ServiceInstance{
		ServiceName: "search",
		InstanceID:  "degraded1",
		Status:      Degraded,
		Metadata:    map[string]string{"version": "v2", "env": "prod"},
		Weight:      5,
	}
	unhealthyInstance := ServiceInstance{
		ServiceName: "search",
		InstanceID:  "unhealthy1",
		Status:      Unhealthy,
		Metadata:    map[string]string{"version": "v1", "env": "staging"},
		Weight:      1,
	}

	registry.RegisterOrUpdate(healthyInstance)
	registry.RegisterOrUpdate(degradedInstance)
	registry.RegisterOrUpdate(unhealthyInstance)

	t.Run("Basic routing", func(t *testing.T) {
		instanceID, err := router.Route("search", nil)
		if err != nil {
			t.Fatalf("Unexpected error: %v", err)
		}
		if instanceID != "healthy1" {
			t.Errorf("Expected healthy instance, got %s", instanceID)
		}
	})

	t.Run("Metadata filtering", func(t *testing.T) {
		instanceID, err := router.Route("search", map[string]string{"version": "v2"})
		if err != nil {
			t.Fatalf("Unexpected error: %v", err)
		}
		if instanceID != "degraded1" {
			t.Errorf("Expected degraded instance with version v2, got %s", instanceID)
		}
	})

	t.Run("No healthy instances", func(t *testing.T) {
		registry.Remove("search", "healthy1")
		registry.Remove("search", "degraded1")

		instanceID, err := router.Route("search", nil)
		if err != nil {
			t.Fatalf("Unexpected error: %v", err)
		}
		if instanceID != "unhealthy1" {
			t.Errorf("Expected unhealthy instance as last resort, got %s", instanceID)
		}
	})

	t.Run("Weighted distribution", func(t *testing.T) {
		registry.RegisterOrUpdate(healthyInstance)
		registry.RegisterOrUpdate(ServiceInstance{
			ServiceName: "search",
			InstanceID:  "healthy2",
			Status:      Healthy,
			Weight:      20,
		})

		count := make(map[string]int)
		for i := 0; i < 1000; i++ {
			instanceID, _ := router.Route("search", nil)
			count[instanceID]++
		}

		ratio := float64(count["healthy2"]) / float64(count["healthy1"])
		if ratio < 1.5 || ratio > 2.5 { // Expecting ~2:1 ratio
			t.Errorf("Weighted distribution failed, ratio was %f", ratio)
		}
	})

	t.Run("Service not found", func(t *testing.T) {
		_, err := router.Route("nonexistent", nil)
		if err == nil {
			t.Error("Expected error for nonexistent service")
		}
	})

	t.Run("No matching metadata", func(t *testing.T) {
		_, err := router.Route("search", map[string]string{"version": "v3"})
		if err == nil {
			t.Error("Expected error for no matching metadata")
		}
	})
}

func TestInstanceExpiration(t *testing.T) {
	registry := NewServiceRegistryWithOptions(RegistryOptions{
		HeartbeatTimeout: 100 * time.Millisecond,
		CleanupInterval:  50 * time.Millisecond,
	})
	router := NewRouter(registry)

	instance := ServiceInstance{
		ServiceName: "auth",
		InstanceID:  "instance1",
		Status:      Healthy,
	}
	registry.RegisterOrUpdate(instance)

	time.Sleep(150 * time.Millisecond)

	_, err := router.Route("auth", nil)
	if err == nil {
		t.Error("Expected error after instance expiration")
	}
}