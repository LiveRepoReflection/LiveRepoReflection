import java.util.*;

public class TaskScheduler {

    private static class Event implements Comparable<Event> {
        int finishTime;
        Task task;
        Machine machine;

        public Event(int finishTime, Task task, Machine machine) {
            this.finishTime = finishTime;
            this.task = task;
            this.machine = machine;
        }

        @Override
        public int compareTo(Event other) {
            return Integer.compare(this.finishTime, other.finishTime);
        }
    }

    public int schedule(List<Task> tasks, List<Machine> machines) {
        if (tasks.isEmpty()) {
            return 0;
        }

        // Pre-check: if no machines are provided, cannot run any tasks.
        if (machines.isEmpty()) {
            throw new IllegalArgumentException("insufficient resources: no machines provided.");
        }

        // Ensure each task can be run on at least one machine.
        for (Task task : tasks) {
            boolean canRun = false;
            for (Machine machine : machines) {
                if (machine.totalCpu >= task.cpuCores && machine.totalMemory >= task.memory) {
                    canRun = true;
                    break;
                }
            }
            if (!canRun) {
                throw new IllegalArgumentException("insufficient resources for task: " + task.id);
            }
        }

        // Build dependency graph and indegree map.
        Map<String, Integer> indegree = new HashMap<>();
        Map<String, List<String>> dependents = new HashMap<>();
        Map<String, Task> taskMap = new HashMap<>();
        for (Task task : tasks) {
            taskMap.put(task.id, task);
            indegree.put(task.id, task.dependencies.size());
            // Initialize dependents list.
            dependents.put(task.id, new ArrayList<>());
        }
        for (Task task : tasks) {
            for (String dep : task.dependencies) {
                if (!dependents.containsKey(dep)) {
                    dependents.put(dep, new ArrayList<>());
                }
                dependents.get(dep).add(task.id);
            }
        }

        // Check for cycles using topological sort.
        Queue<String> topoQueue = new LinkedList<>();
        for (Map.Entry<String, Integer> entry : indegree.entrySet()) {
            if (entry.getValue() == 0) {
                topoQueue.offer(entry.getKey());
            }
        }
        int countVisited = 0;
        while (!topoQueue.isEmpty()) {
            String curr = topoQueue.poll();
            countVisited++;
            for (String dependent : dependents.get(curr)) {
                indegree.put(dependent, indegree.get(dependent) - 1);
                if (indegree.get(dependent) == 0) {
                    topoQueue.offer(dependent);
                }
            }
        }
        if (countVisited != tasks.size()) {
            throw new IllegalArgumentException("cyclic dependency detected.");
        }

        // Reset indegree for scheduling.
        indegree.clear();
        for (Task task : tasks) {
            indegree.put(task.id, task.dependencies.size());
        }

        // Reset machine resource availability.
        for (Machine machine : machines) {
            machine.availableCpu = machine.totalCpu;
            machine.availableMemory = machine.totalMemory;
        }

        // Ready queue for tasks whose dependencies are resolved.
        Queue<Task> readyQueue = new LinkedList<>();
        for (Task task : tasks) {
            if (task.dependencies.isEmpty()) {
                readyQueue.offer(task);
            }
        }

        // Priority queue for events (task completion events).
        PriorityQueue<Event> eventQueue = new PriorityQueue<>();
        int currentTime = 0;
        int makespan = 0;
        int finishedTasks = 0;
        int totalTasks = tasks.size();

        // Set to track tasks that are scheduled (to avoid double-scheduling).
        Set<String> scheduledTasks = new HashSet<>();

        while (finishedTasks < totalTasks) {
            boolean scheduledSomething = false;

            // Attempt to schedule all ready tasks on available machines.
            Iterator<Task> readyIterator = readyQueue.iterator();
            List<Task> tasksScheduledThisRound = new ArrayList<>();
            while (readyIterator.hasNext()) {
                Task task = readyIterator.next();
                boolean scheduled = false;
                // Look for a machine that can run this task.
                for (Machine machine : machines) {
                    if (machine.availableCpu >= task.cpuCores && machine.availableMemory >= task.memory) {
                        // Schedule task on this machine.
                        machine.availableCpu -= task.cpuCores;
                        machine.availableMemory -= task.memory;
                        int finishTime = currentTime + task.executionTime;
                        eventQueue.offer(new Event(finishTime, task, machine));
                        scheduled = true;
                        scheduledTasks.add(task.id);
                        tasksScheduledThisRound.add(task);
                        scheduledSomething = true;
                        break;
                    }
                }
            }
            // Remove tasks that have been scheduled from the ready queue.
            for (Task t : tasksScheduledThisRound) {
                readyQueue.remove(t);
            }

            if (!scheduledSomething) {
                // If no task could be scheduled now, advance time to the next finish event.
                if (eventQueue.isEmpty()) {
                    // Should not happen as cycle detection ensures progress.
                    throw new IllegalStateException("No events to process but tasks remain unscheduled.");
                }
                Event nextEvent = eventQueue.poll();
                currentTime = nextEvent.finishTime;
                makespan = currentTime;
                // Free machine resources.
                Machine machine = nextEvent.machine;
                Task completedTask = nextEvent.task;
                machine.availableCpu += completedTask.cpuCores;
                machine.availableMemory += completedTask.memory;
                finishedTasks++;

                // Process dependents of the finished task.
                List<String> deps = dependents.get(completedTask.id);
                for (String dependentId : deps) {
                    indegree.put(dependentId, indegree.get(dependentId) - 1);
                    if (indegree.get(dependentId) == 0) {
                        readyQueue.offer(taskMap.get(dependentId));
                    }
                }
                // Also process any other events finishing at the same time.
                while (!eventQueue.isEmpty() && eventQueue.peek().finishTime == currentTime) {
                    Event sameTimeEvent = eventQueue.poll();
                    Machine m2 = sameTimeEvent.machine;
                    Task t2 = sameTimeEvent.task;
                    m2.availableCpu += t2.cpuCores;
                    m2.availableMemory += t2.memory;
                    finishedTasks++;
                    List<String> depList = dependents.get(t2.id);
                    for (String depId : depList) {
                        indegree.put(depId, indegree.get(depId) - 1);
                        if (indegree.get(depId) == 0) {
                            readyQueue.offer(taskMap.get(depId));
                        }
                    }
                }
            }
        }
        return makespan;
    }
}