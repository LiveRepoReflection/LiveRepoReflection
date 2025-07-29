package traffic_sim

import (
	"math/rand"
	"sync"
	"time"
)

func init() {
	rand.Seed(time.Now().UnixNano())
}

type intersection struct {
	name     string
	vehicles int
}

type movement struct {
	from     string
	to       string
	vehicles int
}

func SimulateTraffic(network map[string]map[string]int, initialDistribution map[string]int, steps int) map[string]int {
	if steps == 0 {
		return initialDistribution
	}

	// Initialize current state
	current := make(map[string]int)
	for k, v := range initialDistribution {
		current[k] = v
	}

	// Add missing intersections from network with zero vehicles
	for intersection := range network {
		if _, exists := current[intersection]; !exists {
			current[intersection] = 0
		}
	}

	for step := 0; step < steps; step++ {
		current = simulateStep(network, current)
	}

	return current
}

func simulateStep(network map[string]map[string]int, current map[string]int) map[string]int {
	movements := make(chan movement, len(current))
	var wg sync.WaitGroup

	// Calculate movements for each intersection
	for from, vehicles := range current {
		if vehicles > 0 {
			wg.Add(1)
			go func(from string, vehicles int) {
				defer wg.Add(-1)
				calculateMovements(from, vehicles, network, movements)
			}(from, vehicles)
		}
	}

	// Wait for all movement calculations
	go func() {
		wg.Wait()
		close(movements)
	}()

	// Apply movements and create new state
	next := make(map[string]int)
	for k, v := range current {
		next[k] = v
	}

	// Track capacity usage
	capacityUsed := make(map[string]map[string]int)
	for from := range network {
		capacityUsed[from] = make(map[string]int)
		for to := range network[from] {
			capacityUsed[from][to] = 0
		}
	}

	// Collect all movements
	allMovements := make([]movement, 0)
	for m := range movements {
		allMovements = append(allMovements, m)
	}

	// Randomize movement order
	rand.Shuffle(len(allMovements), func(i, j int) {
		allMovements[i], allMovements[j] = allMovements[j], allMovements[i]
	})

	// Apply movements respecting capacity constraints
	for _, m := range allMovements {
		if m.vehicles == 0 {
			continue
		}

		capacity := network[m.from][m.to]
		used := capacityUsed[m.from][m.to]
		available := capacity - used

		if available <= 0 {
			continue
		}

		vehiclesToMove := m.vehicles
		if vehiclesToMove > available {
			vehiclesToMove = available
		}

		next[m.from] -= vehiclesToMove
		next[m.to] += vehiclesToMove
		capacityUsed[m.from][m.to] += vehiclesToMove
	}

	return next
}

func calculateMovements(from string, vehicles int, network map[string]map[string]int, movements chan<- movement) {
	neighbors := make([]string, 0)
	for to, capacity := range network[from] {
		if capacity > 0 {
			neighbors = append(neighbors, to)
		}
	}

	if len(neighbors) == 0 {
		movements <- movement{from: from, to: from, vehicles: vehicles}
		return
	}

	// Randomly distribute vehicles among neighbors
	for _, vehicle := range rand.Perm(vehicles) {
		to := neighbors[vehicle%len(neighbors)]
		movements <- movement{from: from, to: to, vehicles: 1}
	}
}