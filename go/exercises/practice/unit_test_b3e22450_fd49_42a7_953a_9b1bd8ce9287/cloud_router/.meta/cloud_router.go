package cloud_router

import (
	"sync"
)

type RouterSystem struct {
	routers map[string]*router
	mu      sync.RWMutex
}

type router struct {
	rules []*rule
	mu    sync.RWMutex
}

type rule struct {
	id           string
	conditions   map[string]string
	targetRouter string
}

func NewRouterSystem() *RouterSystem {
	return &RouterSystem{
		routers: make(map[string]*router),
	}
}

func (rs *RouterSystem) getOrCreateRouter(routerID string) *router {
	rs.mu.RLock()
	r, exists := rs.routers[routerID]
	rs.mu.RUnlock()

	if !exists {
		rs.mu.Lock()
		defer rs.mu.Unlock()
		// Double check in case another goroutine created it
		if r, exists = rs.routers[routerID]; !exists {
			r = &router{
				rules: make([]*rule, 0),
			}
			rs.routers[routerID] = r
		}
	}
	return r
}

func (rs *RouterSystem) AddRule(routerID, ruleID string, conditions map[string]string, targetRouterID string) {
	r := rs.getOrCreateRouter(routerID)

	r.mu.Lock()
	defer r.mu.Unlock()

	// Check if rule already exists
	for _, existingRule := range r.rules {
		if existingRule.id == ruleID {
			// Update existing rule
			existingRule.conditions = conditions
			existingRule.targetRouter = targetRouterID
			return
		}
	}

	// Add new rule
	r.rules = append(r.rules, &rule{
		id:           ruleID,
		conditions:   conditions,
		targetRouter: targetRouterID,
	})
}

func (rs *RouterSystem) RoutePacket(routerID, destinationIP string, attributes map[string]string) string {
	rs.mu.RLock()
	r, exists := rs.routers[routerID]
	rs.mu.RUnlock()

	if !exists {
		return ""
	}

	r.mu.RLock()
	defer r.mu.RUnlock()

	var bestMatch *rule
	maxConditions := -1

	for _, currentRule := range r.rules {
		matches := 0
		allMatch := true

		// Check if all conditions in the rule match the packet attributes
		for k, v := range currentRule.conditions {
			if attrVal, ok := attributes[k]; ok && attrVal == v {
				matches++
			} else {
				allMatch = false
				break
			}
		}

		if allMatch {
			// Rule with more conditions has higher priority
			if matches > maxConditions {
				maxConditions = matches
				bestMatch = currentRule
			}
		}
	}

	if bestMatch != nil {
		return bestMatch.targetRouter
	}
	return ""
}

func (rs *RouterSystem) RemoveRule(routerID, ruleID string) {
	rs.mu.RLock()
	r, exists := rs.routers[routerID]
	rs.mu.RUnlock()

	if !exists {
		return
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	for i, currentRule := range r.rules {
		if currentRule.id == ruleID {
			// Remove the rule by slicing it out
			r.rules = append(r.rules[:i], r.rules[i+1:]...)
			return
		}
	}
}