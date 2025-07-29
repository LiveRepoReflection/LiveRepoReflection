package task_schedule

import (
	"sort"
)

type Task struct {
	ID          int
	Duration    int
	Deadline    int
	Dependencies []int
}

type Schedule struct {
	TaskID     int
	StartTime  int
	EndTime    int
}

func MinPenaltySchedule(n int, tasks []Task) int {
	// Create a map for quick task lookup
	taskMap := make(map[int]Task)
	for _, task := range tasks {
		taskMap[task.ID] = task
	}

	// Topological sort to determine execution order
	sortedTasks, err := topologicalSort(tasks, taskMap)
	if err != nil {
		return -1 // invalid dependency graph
	}

	// Schedule tasks with earliest deadline first
	schedule := make([]Schedule, 0, n)
	penalty := 0

	for _, task := range sortedTasks {
		// Calculate earliest possible start time based on dependencies
		earliestStart := 0
		for _, depID := range task.Dependencies {
			for _, s := range schedule {
				if s.TaskID == depID && s.EndTime > earliestStart {
					earliestStart = s.EndTime
				}
			}
		}

		// Schedule the task immediately after its dependencies
		startTime := earliestStart
		endTime := startTime + task.Duration

		// Calculate penalty if deadline is missed
		if endTime > task.Deadline {
			penalty += endTime - task.Deadline
		}

		schedule = append(schedule, Schedule{
			TaskID:    task.ID,
			StartTime: startTime,
			EndTime:   endTime,
		})
	}

	return penalty
}

func topologicalSort(tasks []Task, taskMap map[int]Task) ([]Task, error) {
	visited := make(map[int]bool)
	temp := make(map[int]bool)
	order := make([]Task, 0, len(tasks))

	for _, task := range tasks {
		if !visited[task.ID] {
			if err := visit(task.ID, taskMap, visited, temp, &order); err != nil {
				return nil, err
			}
		}
	}

	// Reverse the order to get topological sort
	for i, j := 0, len(order)-1; i < j; i, j = i+1, j-1 {
		order[i], order[j] = order[j], order[i]
	}

	return order, nil
}

func visit(id int, taskMap map[int]Task, visited, temp map[int]bool, order *[]Task) error {
	if temp[id] {
		return nil // skip already processed
	}

	task, exists := taskMap[id]
	if !exists {
		return nil // skip invalid dependencies
	}

	if visited[id] {
		return nil
	}

	temp[id] = true
	for _, depID := range task.Dependencies {
		if err := visit(depID, taskMap, visited, temp, order); err != nil {
			return err
		}
	}

	visited[id] = true
	*order = append(*order, task)
	return nil
}

func earliestDeadlineFirst(tasks []Task) []Task {
	sorted := make([]Task, len(tasks))
	copy(sorted, tasks)

	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].Deadline < sorted[j].Deadline
	})

	return sorted
}