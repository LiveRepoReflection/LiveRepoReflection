package intergalactic_exchange

import (
	"math"
)

type State struct {
	profit  float64
	hops    int
	route   []string
	visited map[string]bool
}

func lexCompare(a, b []string) int {
	minLen := len(a)
	if len(b) < minLen {
		minLen = len(b)
	}
	for i := 0; i < minLen; i++ {
		if a[i] < b[i] {
			return -1
		} else if a[i] > b[i] {
			return 1
		}
	}
	// if all equal so far, compare lengths
	if len(a) < len(b) {
		return -1
	} else if len(a) > len(b) {
		return 1
	}
	return 0
}

// FindOptimalRoute computes the most profitable sequence of star systems to convert
// the initial investment in startSystem's cryptocurrency to endSystem's currency.
// It returns a slice containing the sequence of star systems to visit (including start and end).
// If no route exists, an empty slice is returned.
func FindOptimalRoute(systems map[string]string, rates map[string]map[string]float64, startSystem, endSystem string, initialInvestment float64) []string {
	if startSystem == endSystem {
		if _, ok := systems[startSystem]; ok {
			return []string{startSystem}
		}
		return []string{}
	}

	// Initialize dp: mapping from system to best known state.
	dp := make(map[string]State)
	negInf := math.Inf(-1)
	for sys := range systems {
		dp[sys] = State{
			profit:  negInf,
			hops:    math.MaxInt32,
			route:   nil,
			visited: make(map[string]bool),
		}
	}

	startState := State{
		profit:  math.Log(initialInvestment),
		hops:    0,
		route:   []string{startSystem},
		visited: map[string]bool{startSystem: true},
	}
	dp[startSystem] = startState

	// Use Bellman-Ford relaxation over at most V-1 iterations to avoid cycles.
	V := len(systems)
	updated := true
	for i := 0; i < V-1 && updated; i++ {
		updated = false
		// For each system u with a valid state, try relaxing all edges from u.
		for u, stateU := range dp {
			if stateU.profit == negInf {
				continue
			}
			// Get the currency of system u.
			currU, existsU := systems[u]
			if !existsU {
				continue
			}
			// Try all possible destination systems v.
			for v, currV := range systems {
				if u == v {
					continue
				}
				// Ensure simple paths: do not revisit a system.
				if stateU.visited[v] {
					continue
				}
				var rate float64
				if mp, ok := rates[currU]; ok {
					if r, ok2 := mp[currV]; ok2 {
						rate = r
					} else {
						// Implicit self conversion if currencies match.
						if currU == currV {
							rate = 1.0
						} else {
							continue
						}
					}
				} else {
					if currU == currV {
						rate = 1.0
					} else {
						continue
					}
				}
				newProfit := stateU.profit + math.Log(rate)
				newHops := stateU.hops + 1
				newRoute := make([]string, len(stateU.route))
				copy(newRoute, stateU.route)
				newRoute = append(newRoute, v)
				newVisited := make(map[string]bool)
				for k, val := range stateU.visited {
					newVisited[k] = val
				}
				newVisited[v] = true

				currState := dp[v]
				shouldUpdate := false
				if newProfit > currState.profit {
					shouldUpdate = true
				} else if math.Abs(newProfit-currState.profit) < 1e-9 {
					if newHops < currState.hops {
						shouldUpdate = true
					} else if newHops == currState.hops {
						if lexCompare(newRoute, currState.route) < 0 {
							shouldUpdate = true
						}
					}
				}
				if shouldUpdate {
					dp[v] = State{
						profit:  newProfit,
						hops:    newHops,
						route:   newRoute,
						visited: newVisited,
					}
					updated = true
				}
			}
		}
	}

	finalState, exists := dp[endSystem]
	if exists && finalState.profit != negInf {
		return finalState.route
	}
	return []string{}
}