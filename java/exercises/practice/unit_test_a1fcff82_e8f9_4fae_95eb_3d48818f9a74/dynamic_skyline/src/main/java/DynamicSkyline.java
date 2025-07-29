import java.util.List;

public class DynamicSkyline {
    
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
        
        // Implementation needed
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
        // Implementation needed
    }
    
    /**
     * Returns the current skyline as a list of key points.
     * 
     * @return A list where each element is a list of two integers [x, y]
     *         representing a key point. These are sorted by x coordinate.
     */
    public List<List<Integer>> getSkyline() {
        // Implementation needed
        return null;
    }
}