package resource_scheduler

import (
	"sort"
)

type Task struct {
	cpu, ram, disk, priority int
	sum                      int
}

func ScheduleTasks(n int, m int, workers [][]int, tasks [][]int) int {
	// Convert tasks input to structured Task type.
	taskList := make([]Task, m)
	for i, t := range tasks {
		taskList[i] = Task{
			cpu:      t[0],
			ram:      t[1],
			disk:     t[2],
			priority: t[3],
			sum:      t[0] + t[1] + t[2],
		}
	}

	// Sort tasks primarily by descending priority.
	// For tasks with equal priority, sort them by descending total resource requirement.
	sort.Slice(taskList, func(i, j int) bool {
		if taskList[i].priority == taskList[j].priority {
			return taskList[i].sum > taskList[j].sum
		}
		return taskList[i].priority > taskList[j].priority
	})

	// For scheduling, we use a greedy best-fit strategy.
	// For each task in sorted order, try to assign it to one worker that can accommodate it.
	// Among all feasible workers, choose the worker with minimal leftover
	// (i.e. the sum of remaining resources after assignment) to try to pack resources tightly.
	scheduledCount := 0
	for _, task := range taskList {
		bestIdx := -1
		bestLeftover := 1 << 30
		for i := 0; i < n; i++ {
			avail := workers[i]
			if avail[0] >= task.cpu && avail[1] >= task.ram && avail[2] >= task.disk {
				leftover := (avail[0]-task.cpu) + (avail[1]-task.ram) + (avail[2]-task.disk)
				if leftover < bestLeftover {
					bestLeftover = leftover
					bestIdx = i
				}
			}
		}
		if bestIdx != -1 {
			workers[bestIdx][0] -= task.cpu
			workers[bestIdx][1] -= task.ram
			workers[bestIdx][2] -= task.disk
			scheduledCount++
		}
	}

	return scheduledCount
}