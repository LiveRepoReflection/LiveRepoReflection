import java.util.*;

public class TaskScheduler {

    private static class Event {
        int finishTime;
        String workerId;
        String taskId;

        Event(int finishTime, String workerId, String taskId) {
            this.finishTime = finishTime;
            this.workerId = workerId;
            this.taskId = taskId;
        }
    }

    private static class WorkerAllocation {
        WorkerNode worker;
        int allocatedCpu;
        int allocatedMemory;
        int allocatedDisk;

        WorkerAllocation(WorkerNode worker) {
            this.worker = worker;
            this.allocatedCpu = 0;
            this.allocatedMemory = 0;
            this.allocatedDisk = 0;
        }

        public int availableCpu() {
            return worker.getCpuCapacity() - allocatedCpu;
        }

        public int availableMemory() {
            return worker.getMemoryCapacity() - allocatedMemory;
        }

        public int availableDisk() {
            return worker.getDiskCapacity() - allocatedDisk;
        }

        public void allocate(Task task) {
            allocatedCpu += task.getCpuRequirement();
            allocatedMemory += task.getMemoryRequirement();
            allocatedDisk += task.getDiskRequirement();
        }

        public void release(Task task) {
            allocatedCpu -= task.getCpuRequirement();
            allocatedMemory -= task.getMemoryRequirement();
            allocatedDisk -= task.getDiskRequirement();
        }
    }

    public Schedule scheduleTasks(List<WorkerNode> workerNodes, List<Task> tasks) {
        // Pre-check: Ensure each task can be executed on at least one worker.
        for (Task task : tasks) {
            boolean canBeScheduled = false;
            for (WorkerNode worker : workerNodes) {
                if (task.getCpuRequirement() <= worker.getCpuCapacity() &&
                    task.getMemoryRequirement() <= worker.getMemoryCapacity() &&
                    task.getDiskRequirement() <= worker.getDiskCapacity()) {
                    canBeScheduled = true;
                    break;
                }
            }
            if (!canBeScheduled) {
                return new Schedule(new HashMap<>(), -1);
            }
        }

        // Build dependency graph and indegree map.
        Map<String, List<String>> adj = new HashMap<>();
        Map<String, Integer> indegree = new HashMap<>();
        Map<String, Task> taskMap = new HashMap<>();
        for (Task task : tasks) {
            taskMap.put(task.getId(), task);
            indegree.put(task.getId(), task.getDependencies().size());
            for (String dep : task.getDependencies()) {
                if (!adj.containsKey(dep)) {
                    adj.put(dep, new ArrayList<>());
                }
                adj.get(dep).add(task.getId());
            }
        }

        // Initialize ready queue with zero indegree tasks.
        Queue<String> readyQueue = new LinkedList<>();
        for (Task task : tasks) {
            if (indegree.get(task.getId()) == 0) {
                readyQueue.offer(task.getId());
            }
        }

        // Setup worker allocations.
        Map<String, WorkerAllocation> workerAllocations = new HashMap<>();
        for (WorkerNode worker : workerNodes) {
            workerAllocations.put(worker.getId(), new WorkerAllocation(worker));
        }

        // Priority queue for events sorted by finish time.
        PriorityQueue<Event> eventPQ = new PriorityQueue<>(Comparator.comparingInt(e -> e.finishTime));

        Map<String, String> assignment = new HashMap<>();
        int tasksScheduled = 0;
        int currentTime = 0;
        int makespan = 0;

        while (tasksScheduled < tasks.size()) {
            boolean scheduledSomething = false;
            int readySize = readyQueue.size();
            List<String> unscheduledReadyTasks = new ArrayList<>();
            // Try scheduling every ready task.
            for (int i = 0; i < readySize; i++) {
                String taskId = readyQueue.poll();
                Task task = taskMap.get(taskId);
                boolean scheduled = false;
                for (WorkerAllocation wa : workerAllocations.values()) {
                    if (wa.availableCpu() >= task.getCpuRequirement() &&
                        wa.availableMemory() >= task.getMemoryRequirement() &&
                        wa.availableDisk() >= task.getDiskRequirement()) {
                        // Schedule the task on this worker.
                        wa.allocate(task);
                        int finishTime = currentTime + task.getEstimatedRunTime();
                        eventPQ.offer(new Event(finishTime, wa.worker.getId(), task.getId()));
                        assignment.put(task.getId(), wa.worker.getId());
                        tasksScheduled++;
                        scheduled = true;
                        scheduledSomething = true;
                        makespan = Math.max(makespan, finishTime);
                        break;
                    }
                }
                if (!scheduled) {
                    unscheduledReadyTasks.add(taskId);
                }
            }
            // Put back tasks that couldn't be scheduled due to limited resources.
            for (String tId : unscheduledReadyTasks) {
                readyQueue.offer(tId);
            }
            // If no new scheduling was possible, advance time to next event.
            if (!scheduledSomething) {
                if (eventPQ.isEmpty()) {
                    // No running tasks and still tasks unscheduled implies a cycle or a deadlock.
                    return new Schedule(new HashMap<>(), -1);
                }
                Event nextEvent = eventPQ.poll();
                currentTime = nextEvent.finishTime;
                WorkerAllocation wa = workerAllocations.get(nextEvent.workerId);
                Task finishedTask = taskMap.get(nextEvent.taskId);
                wa.release(finishedTask);
                // Process the completed task's dependent tasks.
                if (adj.containsKey(finishedTask.getId())) {
                    for (String dependent : adj.get(finishedTask.getId())) {
                        indegree.put(dependent, indegree.get(dependent) - 1);
                        if (indegree.get(dependent) == 0) {
                            readyQueue.offer(dependent);
                        }
                    }
                }
                // Process all events finishing at the same time.
                while (!eventPQ.isEmpty() && eventPQ.peek().finishTime == currentTime) {
                    Event e = eventPQ.poll();
                    WorkerAllocation waInner = workerAllocations.get(e.workerId);
                    Task finished = taskMap.get(e.taskId);
                    waInner.release(finished);
                    if (adj.containsKey(finished.getId())) {
                        for (String dependent : adj.get(finished.getId())) {
                            indegree.put(dependent, indegree.get(dependent) - 1);
                            if (indegree.get(dependent) == 0) {
                                readyQueue.offer(dependent);
                            }
                        }
                    }
                }
            }
        }
        return new Schedule(assignment, makespan);
    }
}