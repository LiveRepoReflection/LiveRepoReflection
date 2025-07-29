import java.util.*;
import java.lang.reflect.Field;

public class TaskScheduler {

    public static <T> List<Integer> scheduleTasks(List<T> tasks, List<Integer> cancelledTaskIds) {
        // Initialize reflection cache for required fields: id, processingTime, deadline, dependencies
        Map<String, Field> fieldCache = new HashMap<>();
        if (tasks.isEmpty()) {
            return new ArrayList<>();
        }
        Class<?> taskClass = tasks.get(0).getClass();
        try {
            Field idField = taskClass.getDeclaredField("id");
            idField.setAccessible(true);
            Field ptField = taskClass.getDeclaredField("processingTime");
            ptField.setAccessible(true);
            Field deadlineField = taskClass.getDeclaredField("deadline");
            deadlineField.setAccessible(true);
            Field depsField = taskClass.getDeclaredField("dependencies");
            depsField.setAccessible(true);
            fieldCache.put("id", idField);
            fieldCache.put("processingTime", ptField);
            fieldCache.put("deadline", deadlineField);
            fieldCache.put("dependencies", depsField);
        } catch (NoSuchFieldException e) {
            throw new IllegalArgumentException("Task objects must have id, processingTime, deadline, dependencies fields");
        }

        // Build node map: id -> Node, encapsulating the task information.
        Map<Integer, Node> nodeMap = new HashMap<>();
        for (T taskObj : tasks) {
            try {
                int id = (Integer) fieldCache.get("id").get(taskObj);
                int processingTime = (Integer) fieldCache.get("processingTime").get(taskObj);
                int deadline = (Integer) fieldCache.get("deadline").get(taskObj);
                @SuppressWarnings("unchecked")
                List<Integer> dependencies = (List<Integer>) fieldCache.get("dependencies").get(taskObj);
                Node node = new Node(id, processingTime, deadline, dependencies);
                nodeMap.put(id, node);
            } catch (IllegalAccessException e) {
                throw new RuntimeException(e);
            }
        }

        // Build graph: For each task, add it as a dependent to its dependencies.
        for (Node node : nodeMap.values()) {
            for (Integer depId : node.dependencies) {
                Node depNode = nodeMap.get(depId);
                if (depNode != null) {
                    depNode.dependents.add(node.id);
                }
            }
        }

        // Propagate cancellations: if a task is cancelled, mark all tasks that depend on it (directly or indirectly) as cancelled.
        Set<Integer> cancelledSet = new HashSet<>(cancelledTaskIds);
        Queue<Integer> queue = new LinkedList<>(cancelledTaskIds);
        while (!queue.isEmpty()) {
            int cid = queue.poll();
            Node cancelledNode = nodeMap.get(cid);
            if (cancelledNode != null) {
                for (Integer dependentId : cancelledNode.dependents) {
                    if (!cancelledSet.contains(dependentId)) {
                        cancelledSet.add(dependentId);
                        queue.offer(dependentId);
                    }
                }
            }
        }

        // Remove cancelled nodes from the node map.
        Iterator<Map.Entry<Integer, Node>> iter = nodeMap.entrySet().iterator();
        while (iter.hasNext()){
            Map.Entry<Integer, Node> entry = iter.next();
            if (cancelledSet.contains(entry.getKey())) {
                iter.remove();
            }
        }

        // Compute in-degree for each remaining node (consider only dependencies that are also in the remaining set).
        for (Node node : nodeMap.values()) {
            int count = 0;
            for (Integer depId: node.dependencies) {
                if (nodeMap.containsKey(depId)) {
                    count++;
                }
            }
            node.indegree = count;
        }

        // Topological sort using a priority queue to choose tasks with the earliest deadline among ready tasks.
        PriorityQueue<Node> pq = new PriorityQueue<>(new Comparator<Node>() {
            public int compare(Node n1, Node n2) {
                return Integer.compare(n1.deadline, n2.deadline);
            }
        });

        for (Node node : nodeMap.values()){
            if (node.indegree == 0) {
                pq.offer(node);
            }
        }

        List<Integer> result = new ArrayList<>();
        int processedCount = 0;
        int currentTime = 0;
        while (!pq.isEmpty()){
            Node node = pq.poll();
            result.add(node.id);
            currentTime += node.processingTime;  // Simulate processing time (can be used to assess lateness if needed)
            processedCount++;
            // Reduce in-degree of dependent nodes.
            for (Integer dependentId : node.dependents) {
                Node dependent = nodeMap.get(dependentId);
                if (dependent == null) continue; // Dependent was cancelled or not present.
                if (dependent.dependencies.contains(node.id)) {
                    dependent.indegree--;
                    if (dependent.indegree == 0) {
                        pq.offer(dependent);
                    }
                }
            }
        }

        // If not all nodes were processed, a cycle exists.
        if (processedCount != nodeMap.size()){
            throw new IllegalArgumentException("circular dependencies detected");
        }
        return result;
    }

    // Internal Node class to represent tasks in the scheduling graph.
    private static class Node {
        int id;
        int processingTime;
        int deadline;
        List<Integer> dependencies;
        List<Integer> dependents;
        int indegree;

        Node(int id, int processingTime, int deadline, List<Integer> dependencies) {
            this.id = id;
            this.processingTime = processingTime;
            this.deadline = deadline;
            this.dependencies = new ArrayList<>(dependencies);
            this.dependents = new ArrayList<>();
            this.indegree = 0;
        }
    }
}