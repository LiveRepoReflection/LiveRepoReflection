package optimal_schedule

func OptimalSchedule(deadlines []int, profits []int, dependencies [][]int, maxLateness int) int {
	n := len(deadlines)

	// Define a key to be used for memoization.
	type key struct {
		mask int
		time int
		lat  int
	}

	memo := make(map[key]int)

	var dfs func(mask, time, lat int) int
	dfs = func(mask, time, lat int) int {
		k := key{mask: mask, time: time, lat: lat}
		if val, exists := memo[k]; exists {
			return val
		}

		// Base case: no more tasks can be scheduled.
		best := 0

		// Try every task that is not scheduled yet.
		for i := 0; i < n; i++ {
			// If task i is already scheduled, skip.
			if mask&(1<<i) != 0 {
				continue
			}
			// Ensure that all dependencies for task i have been scheduled.
			canSchedule := true
			for _, dep := range dependencies[i] {
				if mask&(1<<dep) == 0 {
					canSchedule = false
					break
				}
			}
			if !canSchedule {
				continue
			}

			// Calculate the finish time of task i.
			finishTime := time + 1
			addLateness := 0
			if finishTime > deadlines[i] {
				addLateness = finishTime - deadlines[i]
			}
			newLateness := lat + addLateness
			if newLateness > maxLateness {
				continue
			}

			// Schedule task i and update the profit.
			candidate := profits[i] + dfs(mask|(1<<i), time+1, newLateness)
			if candidate > best {
				best = candidate
			}
		}

		memo[k] = best
		return best
	}

	return dfs(0, 0, 0)
}