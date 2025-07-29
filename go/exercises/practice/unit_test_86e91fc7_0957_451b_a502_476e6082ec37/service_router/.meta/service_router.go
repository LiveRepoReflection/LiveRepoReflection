package service_router

import (
	"errors"
	"sync"
	"time"
)

type HealthStatus int

const (
	Healthy HealthStatus = iota
	Degraded
	Unhealthy
)

type ServiceInstance struct {
	ServiceName string
	InstanceID  string
	Status      HealthStatus
	Metadata    map[string]string
	Weight      int
	LastSeen    time.Time
}

type RegistryOptions struct {
	HeartbeatTimeout time.Duration
	CleanupInterval  time.Duration
}

type ServiceRegistry struct {
	instances map[string]map[string]*ServiceInstance
	mu        sync.RWMutex
	options   RegistryOptions
	stopChan  chan struct{}
}

func NewServiceRegistry() *ServiceRegistry {
	return NewServiceRegistryWithOptions(RegistryOptions{
		HeartbeatTimeout: 30 * time.Second,
		CleanupInterval:  10 * time.Second,
	})
}

func NewServiceRegistryWithOptions(options RegistryOptions) *ServiceRegistry {
	r := &ServiceRegistry{
		instances: make(map[string]map[string]*ServiceInstance),
		options:   options,
		stopChan:  make(chan struct{}),
	}
	go r.cleanupExpiredInstances()
	return r
}

func (r *ServiceRegistry) RegisterOrUpdate(instance ServiceInstance) {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.instances[instance.ServiceName]; !exists {
		r.instances[instance.ServiceName] = make(map[string]*ServiceInstance)
	}

	if existing, exists := r.instances[instance.ServiceName][instance.InstanceID]; exists {
		existing.Status = instance.Status
		existing.Metadata = instance.Metadata
		existing.Weight = instance.Weight
		existing.LastSeen = time.Now()
	} else {
		newInstance := instance
		newInstance.LastSeen = time.Now()
		r.instances[instance.ServiceName][instance.InstanceID] = &newInstance
	}
}

func (r *ServiceRegistry) Remove(serviceName, instanceID string) {
	r.mu.Lock()
	defer r.mu.Unlock()

	if instances, exists := r.instances[serviceName]; exists {
		delete(instances, instanceID)
		if len(instances) == 0 {
			delete(r.instances, serviceName)
		}
	}
}

func (r *ServiceRegistry) GetInstances(serviceName string) []ServiceInstance {
	r.mu.RLock()
	defer r.mu.RUnlock()

	serviceInstances := r.instances[serviceName]
	if len(serviceInstances) == 0 {
		return nil
	}

	instances := make([]ServiceInstance, 0, len(serviceInstances))
	for _, instance := range serviceInstances {
		instances = append(instances, *instance)
	}
	return instances
}

func (r *ServiceRegistry) cleanupExpiredInstances() {
	ticker := time.NewTicker(r.options.CleanupInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			r.mu.Lock()
			for serviceName, instances := range r.instances {
				for instanceID, instance := range instances {
					if time.Since(instance.LastSeen) > r.options.HeartbeatTimeout {
						delete(instances, instanceID)
					}
				}
				if len(instances) == 0 {
					delete(r.instances, serviceName)
				}
			}
			r.mu.Unlock()
		case <-r.stopChan:
			return
		}
	}
}

func (r *ServiceRegistry) Stop() {
	close(r.stopChan)
}

type Router struct {
	registry *ServiceRegistry
	counters map[string]int
	mu       sync.Mutex
}

func NewRouter(registry *ServiceRegistry) *Router {
	return &Router{
		registry: registry,
		counters: make(map[string]int),
	}
}

func (r *Router) Route(serviceName string, metadata map[string]string) (string, error) {
	instances := r.registry.GetInstances(serviceName)
	if len(instances) == 0 {
		return "", errors.New("service not found")
	}

	var candidates []ServiceInstance
	for _, instance := range instances {
		if matchesMetadata(instance, metadata) {
			candidates = append(candidates, instance)
		}
	}

	if len(candidates) == 0 {
		return "", errors.New("no instances matching metadata")
	}

	healthy, degraded, unhealthy := categorizeInstances(candidates)
	selectedGroup := healthy
	if len(healthy) == 0 {
		selectedGroup = degraded
		if len(degraded) == 0 {
			selectedGroup = unhealthy
			if len(unhealthy) == 0 {
				return "", errors.New("no available instances")
			}
		}
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	key := serviceName + hashMetadata(metadata)
	r.counters[key]++

	totalWeight := 0
	for _, instance := range selectedGroup {
		totalWeight += instance.Weight
	}

	if totalWeight == 0 {
		return selectedGroup[0].InstanceID, nil
	}

	current := r.counters[key] % totalWeight
	for _, instance := range selectedGroup {
		if current < instance.Weight {
			return instance.InstanceID, nil
		}
		current -= instance.Weight
	}

	return selectedGroup[0].InstanceID, nil
}

func matchesMetadata(instance ServiceInstance, metadata map[string]string) bool {
	if len(metadata) == 0 {
		return true
	}

	for k, v := range metadata {
		if instance.Metadata == nil || instance.Metadata[k] != v {
			return false
		}
	}
	return true
}

func categorizeInstances(instances []ServiceInstance) (healthy, degraded, unhealthy []ServiceInstance) {
	for _, instance := range instances {
		switch instance.Status {
		case Healthy:
			healthy = append(healthy, instance)
		case Degraded:
			degraded = append(degraded, instance)
		case Unhealthy:
			unhealthy = append(unhealthy, instance)
		}
	}
	return
}

func hashMetadata(metadata map[string]string) string {
	if len(metadata) == 0 {
		return ""
	}
	var hash string
	for k, v := range metadata {
		hash += k + "=" + v + ";"
	}
	return hash
}