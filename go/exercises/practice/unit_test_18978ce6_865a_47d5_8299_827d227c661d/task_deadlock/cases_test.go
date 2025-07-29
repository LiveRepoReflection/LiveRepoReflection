package task_deadlock

type Task struct {
	ID           int
	Dependencies []int
}