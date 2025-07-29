import java.util.*;

public class DynamicSkyline {
    // We use a TreeMap to track critical points in the skyline for each building
    // The key is the x-coordinate, and the value is a map tracking heights and their counts
    private final TreeMap<Integer, TreeMap<Integer, Integer>> criticalPoints;
    
    // Keep track of buildings for removal operations
    private final Map<Building, Integer> buildings;
    
    /**
     * Constructor for DynamicSkyline.
     */
    public DynamicSkyline() {
        this.criticalPoints = new TreeMap<>();
        this.buildings = new HashMap<>();
    }
    
    /**
     * Adds a building to the city.
     * 
     * @param left The left x-coordinate of the building
     * @param right The right x-coordinate of the building
     * @param height The height of the building
     * @throws IllegalArgumentException if left >= right or height <= 0
     */
    public void addBuilding(int left, int right, int height) {
        if (left >= right) {
            throw new IllegalArgumentException("left must be less than right");
        }
        if (height <= 0) {
            throw new IllegalArgumentException("height must be positive");
        }
        
        // Create building object and add to buildings map
        Building building = new Building(left, right, height);
        buildings.put(building, buildings.getOrDefault(building, 0) + 1);
        
        // Update critical points at left (start) coordinate
        criticalPoints.putIfAbsent(left, new TreeMap<>());
        TreeMap<Integer, Integer> leftHeights = criticalPoints.get(left);
        leftHeights.put(height, leftHeights.getOrDefault(height, 0) + 1);
        
        // Update critical points at right (end) coordinate
        criticalPoints.putIfAbsent(right, new TreeMap<>());
        TreeMap<Integer, Integer> rightHeights = criticalPoints.get(right);
        rightHeights.put(-height, rightHeights.getOrDefault(-height, 0) + 1); // Negative height denotes removal
    }
    
    /**
     * Removes a building from the city.
     * 
     * @param left The left x-coordinate of the building
     * @param right The right x-coordinate of the building
     * @param height The height of the building
     * @throws IllegalArgumentException if the building does not exist
     */
    public void removeBuilding(int left, int right, int height) {
        Building building = new Building(left, right, height);
        
        // Check if building exists
        if (!buildings.containsKey(building) || buildings.get(building) <= 0) {
            throw new IllegalArgumentException("Building does not exist");
        }
        
        // Update count in buildings map
        int count = buildings.get(building);
        if (count == 1) {
            buildings.remove(building);
        } else {
            buildings.put(building, count - 1);
        }
        
        // Update critical points at left (start) coordinate
        TreeMap<Integer, Integer> leftHeights = criticalPoints.get(left);
        int leftCount = leftHeights.get(height);
        if (leftCount == 1) {
            leftHeights.remove(height);
            if (leftHeights.isEmpty()) {
                criticalPoints.remove(left);
            }
        } else {
            leftHeights.put(height, leftCount - 1);
        }
        
        // Update critical points at right (end) coordinate
        TreeMap<Integer, Integer> rightHeights = criticalPoints.get(right);
        int rightCount = rightHeights.get(-height);
        if (rightCount == 1) {
            rightHeights.remove(-height);
            if (rightHeights.isEmpty()) {
                criticalPoints.remove(right);
            }
        } else {
            rightHeights.put(-height, rightCount - 1);
        }
    }
    
    /**
     * Returns the current skyline as a list of key points.
     * 
     * @return A list where each element is a list of two integers [x, y]
     *         representing a key point. These are sorted by x coordinate.
     */
    public List<List<Integer>> getSkyline() {
        List<List<Integer>> result = new ArrayList<>();
        if (criticalPoints.isEmpty()) {
            return result;
        }
        
        // Use a TreeMap to keep track of current heights (with counts)
        TreeMap<Integer, Integer> heightsCount = new TreeMap<>();
        int prevHeight = 0;
        
        // Process all critical points in order of x-coordinate
        for (Map.Entry<Integer, TreeMap<Integer, Integer>> entry : criticalPoints.entrySet()) {
            int x = entry.getKey();
            TreeMap<Integer, Integer> heights = entry.getValue();
            
            // Process all height changes at this x-coordinate
            for (Map.Entry<Integer, Integer> heightEntry : heights.entrySet()) {
                int h = heightEntry.getKey();
                int count = heightEntry.getValue();
                
                if (h > 0) {
                    // Add height
                    heightsCount.put(h, heightsCount.getOrDefault(h, 0) + count);
                } else {
                    // Remove height (h is negative for removal points)
                    int actualHeight = -h;
                    int currentCount = heightsCount.get(actualHeight);
                    if (currentCount == count) {
                        heightsCount.remove(actualHeight);
                    } else {
                        heightsCount.put(actualHeight, currentCount - count);
                    }
                }
            }
            
            // Get current max height after processing this x-coordinate
            int currentHeight = heightsCount.isEmpty() ? 0 : heightsCount.lastKey();
            
            // Only add to result if height has changed
            if (currentHeight != prevHeight) {
                result.add(Arrays.asList(x, currentHeight));
                prevHeight = currentHeight;
            }
        }
        
        return result;
    }
    
    /**
     * Represents a building in the city.
     */
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
}