import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;
import java.util.Queue;

public class TaskScheduler {

    // This method uses reflection to access the fields of the task objects.
    // It expects each task object to have the following fields:
    // int id, int duration, int deadline, and List<Integer> dependencies.
    public static int minPenalty(List<?> tasks) {
        if (tasks == null || tasks.isEmpty()) {
            return 0;
        }
        
        // Create a mapping from task id to Node.
        Map<Integer, Node> nodeMap = new HashMap<>();
        
        // First pass: create nodes for each task.
        for (Object task : tasks) {
            int id = getIntField(task, "id");
            int duration = getIntField(task, "duration");
            int deadline = getIntField(task, "deadline");
            @SuppressWarnings("unchecked")
            List<Integer> dependencies = (List<Integer>) getField(task, "dependencies");
            if(dependencies == null) {
                dependencies = new ArrayList<>();
            }
            Node node = new Node(id, duration, deadline, dependencies);
            if (nodeMap.containsKey(id)) {
                // Duplicate task id, ignore or override.
                nodeMap.put(id, node);
            } else {
                nodeMap.put(id, node);
            }
        }
        
        // Second pass: build graph links and compute in-degrees.
        for (Node node : nodeMap.values()) {
            for (Integer depId : node.dependencies) {
                Node depNode = nodeMap.get(depId);
                if (depNode == null) {
                    // dependency not found: invalid input, return maximum penalty.
                    return Integer.MAX_VALUE;
                }
                depNode.successors.add(node);
                node.inDegree++;
            }
        }
        
        // Use a priority queue to select the next task.
        // Priority is defined by task deadline (earliest deadline first).
        Queue<Node> available = new PriorityQueue<>((a, b) -> Integer.compare(a.deadline, b.deadline));
        
        // Add all tasks with inDegree 0.
        for (Node node : nodeMap.values()) {
            if (node.inDegree == 0) {
                available.offer(node);
            }
        }
        
        int currentTime = 0;
        int totalPenalty = 0;
        int processedCount = 0;
        
        while (!available.isEmpty()) {
            Node curr = available.poll();
            processedCount++;
            currentTime += curr.duration;
            if (currentTime > curr.deadline) {
                totalPenalty += (currentTime - curr.deadline);
            }
            
            // For each successor, reduce indegree and add to queue if it becomes 0.
            for (Node succ : curr.successors) {
                succ.inDegree--;
                if (succ.inDegree == 0) {
                    available.offer(succ);
                }
            }
        }
        
        // If not all tasks were processed, there is a cycle or unsatisfied dependency.
        if (processedCount != tasks.size()) {
            return Integer.MAX_VALUE;
        }
        
        return totalPenalty;
    }
    
    // Helper method to get an int field using reflection.
    private static int getIntField(Object obj, String fieldName) {
        Object value = getField(obj, fieldName);
        if (value instanceof Integer) {
            return (Integer)value;
        }
        throw new RuntimeException("Field " + fieldName + " is not an int in object: " + obj);
    }
    
    // Helper method to get a field value using reflection.
    private static Object getField(Object obj, String fieldName) {
        try {
            Field field = getDeclaredFieldIncludingSuper(obj.getClass(), fieldName);
            field.setAccessible(true);
            return field.get(obj);
        } catch (Exception e) {
            throw new RuntimeException("Failed to get field " + fieldName + " from object: " + obj, e);
        }
    }
    
    // This method searches for a declared field in the class or its superclasses.
    private static Field getDeclaredFieldIncludingSuper(Class<?> clazz, String fieldName) throws NoSuchFieldException {
        Class<?> curr = clazz;
        while (curr != null) {
            try {
                return curr.getDeclaredField(fieldName);
            } catch (NoSuchFieldException e) {
                curr = curr.getSuperclass();
            }
        }
        throw new NoSuchFieldException("Field " + fieldName + " not found in class hierarchy of " + clazz.getName());
    }
    
    // Internal Node class used for scheduling.
    private static class Node {
        int id;
        int duration;
        int deadline;
        List<Integer> dependencies;
        List<Node> successors;
        int inDegree;
        
        Node(int id, int duration, int deadline, List<Integer> dependencies) {
            this.id = id;
            this.duration = duration;
            this.deadline = deadline;
            this.dependencies = dependencies;
            this.successors = new ArrayList<>();
            this.inDegree = 0;
        }
    }
}