package optimal_tasks

type Task struct {
	ID          int
	Duration    int
	Deadline    int
	Dependencies []int
}

func OptimalSchedule(tasks []Task) []int {
	// Build dependency graph and in-degree count
	graph := make(map[int][]int)
	inDegree := make(map[int]int)
	taskMap := make(map[int]Task)

	for _, task := range tasks {
		taskMap[task.ID] = task
		inDegree[task.ID] = 0
	}

	for _, task := range tasks {
		for _, dep := range task.Dependencies {
			graph[dep] = append(graph[dep], task.ID)
			inDegree[task.ID]++
		}
	}

	// Initialize queue with tasks having no dependencies
	var queue []int
	for id, deg := range inDegree {
		if deg == 0 {
			queue = append(queue, id)
		}
	}

	// Kahn's algorithm for topological sort
	var order []int
	for len(queue) > 0 {
		// Find task with earliest deadline
		minIndex := 0
		for i := 1; i < len(queue); i++ {
			if taskMap[queue[i]].Deadline < taskMap[queue[minIndex]].Deadline {
				minIndex = i
			}
		}

		current := queue[minIndex]
		queue = append(queue[:minIndex], queue[minIndex+1:]...)
		order = append(order, current)

		// Decrement in-degree of neighbors
		for _, neighbor := range graph[current] {
			inDegree[neighbor]--
			if inDegree[neighbor] == 0 {
				queue = append(queue, neighbor)
			}
		}
	}

	return order
}