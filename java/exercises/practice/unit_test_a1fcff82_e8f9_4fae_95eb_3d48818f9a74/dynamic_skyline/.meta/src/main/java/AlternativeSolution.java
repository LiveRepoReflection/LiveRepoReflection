import java.util.*;

/**
 * An alternative implementation of the DynamicSkyline using a sweep line algorithm
 * with a priority queue approach. This implementation is provided for comparison
 * purposes and demonstrates another valid approach to the problem.
 */
public class AlternativeSolution {
    // Store buildings for easy removal
    private final Map<Building, Integer> buildings;
    
    public AlternativeSolution() {
        this.buildings = new HashMap<>();
    }
    
    public void addBuilding(int left, int right, int height) {
        if (left >= right) {
            throw new IllegalArgumentException("left must be less than right");
        }
        if (height <= 0) {
            throw new IllegalArgumentException("height must be positive");
        }
        
        Building building = new Building(left, right, height);
        buildings.put(building, buildings.getOrDefault(building, 0) + 1);
    }
    
    public void removeBuilding(int left, int right, int height) {
        Building building = new Building(left, right, height);
        if (!buildings.containsKey(building) || buildings.get(building) <= 0) {
            throw new IllegalArgumentException("Building does not exist");
        }
        
        int count = buildings.get(building);
        if (count == 1) {
            buildings.remove(building);
        } else {
            buildings.put(building, count - 1);
        }
    }
    
    public List<List<Integer>> getSkyline() {
        List<List<Integer>> result = new ArrayList<>();
        if (buildings.isEmpty()) {
            return result;
        }
        
        // Create list of all critical points
        List<Point> points = new ArrayList<>();
        
        for (Map.Entry<Building, Integer> entry : buildings.entrySet()) {
            Building building = entry.getKey();
            int count = entry.getValue();
            
            for (int i = 0; i < count; i++) {
                points.add(new Point(building.left, building.height, true));  // start point
                points.add(new Point(building.right, building.height, false)); // end point
            }
        }
        
        // Sort points by x-coordinate, with tiebreakers
        Collections.sort(points);
        
        // Process points with a height heap
        PriorityQueue<Integer> heightHeap = new PriorityQueue<>(Collections.reverseOrder());  // max-heap for heights
        heightHeap.offer(0);  // ground level
        
        int prevMaxHeight = 0;
        
        for (Point point : points) {
            if (point.isStart) {
                heightHeap.offer(point.height);
            } else {
                heightHeap.remove(point.height);  // O(n) operation, but can be improved
            }
            
            int currentMaxHeight = heightHeap.peek();
            if (currentMaxHeight != prevMaxHeight) {
                result.add(Arrays.asList(point.x, currentMaxHeight));
                prevMaxHeight = currentMaxHeight;
            }
        }
        
        return result;
    }
    
    private static class Building {
        final int left;
        final int right;
        final int height;
        
        Building(int left, int right, int height) {
            this.left = left;
            this.right = right;
            this.height = height;
        }
        
        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (o == null || getClass() != o.getClass()) return false;
            Building building = (Building) o;
            return left == building.left && right == building.right && height == building.height;
        }
        
        @Override
        public int hashCode() {
            return Objects.hash(left, right, height);
        }
    }
    
    private static class Point implements Comparable<Point> {
        final int x;
        final int height;
        final boolean isStart;
        
        Point(int x, int height, boolean isStart) {
            this.x = x;
            this.height = height;
            this.isStart = isStart;
        }
        
        @Override
        public int compareTo(Point other) {
            // First sort by x-coordinate
            if (this.x != other.x) {
                return Integer.compare(this.x, other.x);
            }
            
            // If x is the same, sort by start/end:
            // - Start points come before end points
            if (this.isStart != other.isStart) {
                return this.isStart ? -1 : 1;
            }
            
            // If both are start points, higher buildings come first
            if (this.isStart) {
                return Integer.compare(other.height, this.height);
            } 
            // If both are end points, lower buildings come first
            else {
                return Integer.compare(this.height, other.height);
            }
        }
    }
}