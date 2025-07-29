import java.util.*;

public class TaskScheduler {
    private final List<Node> nodes;
    private final List<Task> tasks;
    private final List<Pair<Task, Task>> dependencies;
    private final Map<Task, Set<Task>> dependencyGraph;
    private final Map<Task, Integer> inDegree;

    public TaskScheduler(List<Node> nodes, List<Task> tasks, List<Pair<Task, Task>> dependencies) {
        this.nodes = new ArrayList<>(nodes);
        this.tasks = new ArrayList<>(tasks);
        this.dependencies = new ArrayList<>(dependencies);
        this.dependencyGraph = buildDependencyGraph();
        this.inDegree = calculateInDegree();
    }

    private Map<Task, Set<Task>> buildDependencyGraph() {
        Map<Task, Set<Task>> graph = new HashMap<>();
        for (Task task : tasks) {
            graph.put(task, new HashSet<>());
        }
        for (Pair<Task, Task> dep : dependencies) {
            graph.get(dep.getFirst()).add(dep.getSecond());
        }
        return graph;
    }

    private Map<Task, Integer> calculateInDegree() {
        Map<Task, Integer> inDegree = new HashMap<>();
        for (Task task : tasks) {
            inDegree.put(task, 0);
        }
        for (Pair<Task, Task> dep : dependencies) {
            inDegree.merge(dep.getSecond(), 1, Integer::sum);
        }
        return inDegree;
    }

    public Map<Task, Assignment> schedule() {
        // Check for cyclic dependencies
        if (hasCycle()) {
            throw new IllegalStateException("Cyclic dependencies detected");
        }

        Map<Task, Assignment> schedule = new HashMap<>();
        PriorityQueue<TaskWithStartTime> readyTasks = new PriorityQueue<>(
            Comparator.comparingInt(TaskWithStartTime::getStartTime)
        );

        // Initialize with tasks that have no dependencies
        for (Task task : tasks) {
            if (inDegree.get(task) == 0) {
                readyTasks.offer(new TaskWithStartTime(task, 0));
            }
        }

        // Track resource usage over time for each node
        Map<Node, List<ResourceUsage>> nodeResources = new HashMap<>();
        for (Node node : nodes) {
            nodeResources.put(node, new ArrayList<>());
        }

        while (!readyTasks.isEmpty()) {
            TaskWithStartTime currentTask = readyTasks.poll();
            Task task = currentTask.getTask();
            int earliestStartTime = currentTask.getStartTime();

            // Find suitable node and time slot
            Assignment assignment = findSuitableAssignment(task, earliestStartTime, nodeResources);
            if (assignment == null) {
                throw new IllegalStateException("No feasible schedule found");
            }

            // Update schedule and resource usage
            schedule.put(task, assignment);
            updateResourceUsage(nodeResources, assignment, task);

            // Process dependent tasks
            for (Task dependent : dependencyGraph.get(task)) {
                inDegree.put(dependent, inDegree.get(dependent) - 1);
                if (inDegree.get(dependent) == 0) {
                    int dependentStartTime = assignment.getStartTimeSeconds() + task.getExecutionTimeSeconds();
                    readyTasks.offer(new TaskWithStartTime(dependent, dependentStartTime));
                }
            }
        }

        if (schedule.size() != tasks.size()) {
            throw new IllegalStateException("Unable to schedule all tasks");
        }

        return schedule;
    }

    private boolean hasCycle() {
        Set<Task> visited = new HashSet<>();
        Set<Task> recursionStack = new HashSet<>();

        for (Task task : tasks) {
            if (hasCycleDFS(task, visited, recursionStack)) {
                return true;
            }
        }
        return false;
    }

    private boolean hasCycleDFS(Task task, Set<Task> visited, Set<Task> recursionStack) {
        if (recursionStack.contains(task)) {
            return true;
        }
        if (visited.contains(task)) {
            return false;
        }

        visited.add(task);
        recursionStack.add(task);

        for (Task dependent : dependencyGraph.get(task)) {
            if (hasCycleDFS(dependent, visited, recursionStack)) {
                return true;
            }
        }

        recursionStack.remove(task);
        return false;
    }

    private Assignment findSuitableAssignment(
        Task task,
        int earliestStartTime,
        Map<Node, List<ResourceUsage>> nodeResources
    ) {
        Assignment bestAssignment = null;
        double bestUtilization = Double.MAX_VALUE;

        for (Node node : nodes) {
            if (!hasRequiredResources(node, task)) {
                continue;
            }

            int startTime = findEarliestStartTime(node, task, earliestStartTime, nodeResources.get(node));
            if (startTime >= 0) {
                double utilization = calculateNodeUtilization(node, nodeResources.get(node), startTime);
                if (bestAssignment == null || utilization < bestUtilization) {
                    bestAssignment = new Assignment(node, startTime);
                    bestUtilization = utilization;
                }
            }
        }

        return bestAssignment;
    }

    private boolean hasRequiredResources(Node node, Task task) {
        return node.getCpuCores() >= task.getCpuCoresRequired() &&
               node.getMemoryGB() >= task.getMemoryGBRequired() &&
               node.getGpuCount() >= task.getGpuCountRequired();
    }

    private int findEarliestStartTime(
        Node node,
        Task task,
        int earliestPossibleStart,
        List<ResourceUsage> resourceUsages
    ) {
        int currentTime = earliestPossibleStart;
        boolean found = false;

        while (!found) {
            boolean conflict = false;
            for (ResourceUsage usage : resourceUsages) {
                if (usage.overlaps(currentTime, task.getExecutionTimeSeconds())) {
                    if (!usage.hasEnoughResources(node, task)) {
                        currentTime = usage.endTime;
                        conflict = true;
                        break;
                    }
                }
            }
            if (!conflict) {
                found = true;
            }
        }

        return currentTime;
    }

    private double calculateNodeUtilization(Node node, List<ResourceUsage> resourceUsages, int time) {
        int totalCpuUsage = 0;
        for (ResourceUsage usage : resourceUsages) {
            if (usage.overlaps(time, 0)) {
                totalCpuUsage += usage.cpuCores;
            }
        }
        return (double) totalCpuUsage / node.getCpuCores();
    }

    private void updateResourceUsage(
        Map<Node, List<ResourceUsage>> nodeResources,
        Assignment assignment,
        Task task
    ) {
        List<ResourceUsage> usages = nodeResources.get(assignment.getNode());
        usages.add(new ResourceUsage(
            assignment.getStartTimeSeconds(),
            assignment.getStartTimeSeconds() + task.getExecutionTimeSeconds(),
            task.getCpuCoresRequired(),
            task.getMemoryGBRequired(),
            task.getGpuCountRequired()
        ));
        usages.sort(Comparator.comparingInt(u -> u.startTime));
    }

    private static class TaskWithStartTime {
        private final Task task;
        private final int startTime;

        TaskWithStartTime(Task task, int startTime) {
            this.task = task;
            this.startTime = startTime;
        }

        Task getTask() {
            return task;
        }

        int getStartTime() {
            return startTime;
        }
    }

    private static class ResourceUsage {
        final int startTime;
        final int endTime;
        final int cpuCores;
        final int memoryGB;
        final int gpuCount;

        ResourceUsage(int startTime, int endTime, int cpuCores, int memoryGB, int gpuCount) {
            this.startTime = startTime;
            this.endTime = endTime;
            this.cpuCores = cpuCores;
            this.memoryGB = memoryGB;
            this.gpuCount = gpuCount;
        }

        boolean overlaps(int time, int duration) {
            return time < endTime && (time + duration) > startTime;
        }

        boolean hasEnoughResources(Node node, Task task) {
            return (node.getCpuCores() - cpuCores) >= task.getCpuCoresRequired() &&
                   (node.getMemoryGB() - memoryGB) >= task.getMemoryGBRequired() &&
                   (node.getGpuCount() - gpuCount) >= task.getGpuCountRequired();
        }
    }
}