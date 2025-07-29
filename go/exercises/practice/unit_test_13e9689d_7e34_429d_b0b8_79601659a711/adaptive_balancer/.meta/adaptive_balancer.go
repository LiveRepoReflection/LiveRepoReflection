package adaptive_balancer

import (
	"sync"
)

type ServerInfo struct {
	id       string
	capacity int
	regOrder int
	cpuUsage int
	latency  int
}

type LoadBalancer struct {
	mu           sync.RWMutex
	servers      map[string]*ServerInfo
	orderCounter int
}

func (lb *LoadBalancer) RegisterServer(serverID string, capacity int) {
	lb.mu.Lock()
	defer lb.mu.Unlock()
	if lb.servers == nil {
		lb.servers = make(map[string]*ServerInfo)
	}
	lb.servers[serverID] = &ServerInfo{
		id:       serverID,
		capacity: capacity,
		regOrder: lb.orderCounter,
		cpuUsage: 0,
		latency:  0,
	}
	lb.orderCounter++
}

func (lb *LoadBalancer) RemoveServer(serverID string) {
	lb.mu.Lock()
	defer lb.mu.Unlock()
	if lb.servers != nil {
		delete(lb.servers, serverID)
	}
}

func (lb *LoadBalancer) ReceiveMetrics(serverMetrics map[string]int, latencyMetrics map[string]int) {
	lb.mu.Lock()
	defer lb.mu.Unlock()
	if lb.servers == nil {
		return
	}
	for id, server := range lb.servers {
		if load, ok := serverMetrics[id]; ok {
			server.cpuUsage = load
		}
		if lat, ok := latencyMetrics[id]; ok {
			server.latency = lat
		}
	}
}

func (lb *LoadBalancer) RouteRequest() string {
	lb.mu.RLock()
	defer lb.mu.RUnlock()
	var candidate *ServerInfo
	for _, server := range lb.servers {
		if server.cpuUsage >= 90 {
			continue
		}
		if candidate == nil {
			candidate = server
			continue
		}
		if server.cpuUsage < candidate.cpuUsage {
			candidate = server
		} else if server.cpuUsage == candidate.cpuUsage {
			if server.latency < candidate.latency {
				candidate = server
			} else if server.latency == candidate.latency {
				if server.regOrder < candidate.regOrder {
					candidate = server
				}
			}
		}
	}
	if candidate == nil {
		return ""
	}
	return candidate.id
}