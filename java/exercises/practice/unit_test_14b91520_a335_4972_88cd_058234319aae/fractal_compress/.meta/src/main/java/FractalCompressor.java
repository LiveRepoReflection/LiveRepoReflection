import java.util.ArrayList;
import java.util.List;

/**
 * This class implements a simplified fractal image compression algorithm.
 * It finds self-similarities within an image and represents the image as 
 * a set of transformations from domain blocks to range blocks.
 */
public class FractalCompressor {

    /**
     * Compresses the given grayscale image using fractal compression.
     *
     * @param image The input image as a 2D array of integers (0-255)
     * @param rangeSize The size of each range block (must be a power of 2)
     * @param stride The stride to use when creating domain blocks
     * @return A list of transformations representing the fractal compression
     * @throws IllegalArgumentException if the input parameters are invalid
     */
    public List<Transformation> compress(int[][] image, int rangeSize, int stride) {
        // Validate input
        validateInput(image, rangeSize, stride);
        
        int height = image.length;
        int width = image[0].length;
        int domainSize = 2 * rangeSize;
        
        List<Transformation> transformations = new ArrayList<>();
        
        // Process each range block
        for (int rangeRow = 0; rangeRow < height; rangeRow += rangeSize) {
            for (int rangeCol = 0; rangeCol < width; rangeCol += rangeSize) {
                // Extract the current range block
                int[][] rangeBlock = extractBlock(image, rangeRow, rangeCol, rangeSize);
                
                // Find the best matching domain block for this range block
                Transformation bestTransformation = findBestDomainBlock(
                    image, rangeBlock, rangeRow, rangeCol, rangeSize, domainSize, stride);
                
                transformations.add(bestTransformation);
            }
        }
        
        return transformations;
    }
    
    /**
     * Validates the input parameters for the compression algorithm.
     *
     * @param image The input image
     * @param rangeSize The size of each range block
     * @param stride The stride to use when creating domain blocks
     * @throws IllegalArgumentException if any parameter is invalid
     */
    private void validateInput(int[][] image, int rangeSize, int stride) {
        // Check if image is empty
        if (image == null || image.length == 0 || image[0].length == 0) {
            throw new IllegalArgumentException("Image cannot be empty");
        }
        
        int height = image.length;
        int width = image[0].length;
        
        // Check if image dimensions are powers of 2
        if (!isPowerOfTwo(height) || !isPowerOfTwo(width)) {
            throw new IllegalArgumentException("Image dimensions must be powers of 2");
        }
        
        // Check if rangeSize is a power of 2
        if (!isPowerOfTwo(rangeSize)) {
            throw new IllegalArgumentException("Range size must be a power of 2");
        }
        
        // Check if rangeSize is valid
        if (rangeSize < 1 || rangeSize > Math.min(height, width) / 2) {
            throw new IllegalArgumentException("Invalid range size");
        }
        
        // Check if stride is valid
        if (stride < 1 || stride > rangeSize) {
            throw new IllegalArgumentException("Invalid stride");
        }
        
        // Check if all rows have the same length
        for (int i = 0; i < height; i++) {
            if (image[i].length != width) {
                throw new IllegalArgumentException("Image must be rectangular");
            }
        }
    }
    
    /**
     * Checks if a number is a power of 2.
     *
     * @param n The number to check
     * @return true if n is a power of 2, false otherwise
     */
    private boolean isPowerOfTwo(int n) {
        return n > 0 && (n & (n - 1)) == 0;
    }
    
    /**
     * Extracts a block from the image starting at the specified position.
     *
     * @param image The source image
     * @param startRow The starting row
     * @param startCol The starting column
     * @param size The size of the block
     * @return The extracted block as a 2D array
     */
    private int[][] extractBlock(int[][] image, int startRow, int startCol, int size) {
        int[][] block = new int[size][size];
        
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                if (startRow + i < image.length && startCol + j < image[0].length) {
                    block[i][j] = image[startRow + i][startCol + j];
                }
            }
        }
        
        return block;
    }
    
    /**
     * Finds the best matching domain block for a given range block.
     *
     * @param image The source image
     * @param rangeBlock The range block to match
     * @param rangeRow The row of the range block in the original image
     * @param rangeCol The column of the range block in the original image
     * @param rangeSize The size of the range block
     * @param domainSize The size of the domain block
     * @param stride The stride to use when searching for domain blocks
     * @return The transformation that best maps a domain block to the range block
     */
    private Transformation findBestDomainBlock(int[][] image, int[][] rangeBlock, 
                                             int rangeRow, int rangeCol,
                                             int rangeSize, int domainSize, int stride) {
        int height = image.length;
        int width = image[0].length;
        
        Transformation bestTransformation = null;
        double minError = Double.MAX_VALUE;
        
        // Iterate over all possible domain blocks with the given stride
        for (int domainRow = 0; domainRow <= height - domainSize; domainRow += stride) {
            for (int domainCol = 0; domainCol <= width - domainSize; domainCol += stride) {
                // Extract the domain block
                int[][] domainBlock = extractBlock(image, domainRow, domainCol, domainSize);
                
                // Downsample the domain block
                int[][] downsampledDomain = downsampleBlock(domainBlock);
                
                // Try different transformations
                for (int rotation : new int[]{0, 90, 180, 270}) {
                    for (boolean flip : new boolean[]{false, true}) {
                        // Apply geometric transformation
                        int[][] transformedDomain = applyGeometricTransformation(downsampledDomain, rotation, flip);
                        
                        // Find optimal contrast scaling and brightness offset
                        double[] params = findOptimalParameters(rangeBlock, transformedDomain);
                        double scale = params[0];
                        double offset = params[1];
                        
                        // Calculate the error (RMSE)
                        double error = calculateRMSE(rangeBlock, transformedDomain, scale, offset);
                        
                        // Update if this is the best transformation so far
                        if (error < minError) {
                            minError = error;
                            bestTransformation = new Transformation(
                                rangeRow, rangeCol, domainRow, domainCol, 
                                rotation, flip, scale, offset, error);
                        }
                    }
                }
            }
        }
        
        return bestTransformation;
    }
    
    /**
     * Downsamples a block by averaging 2x2 regions.
     *
     * @param block The block to downsample
     * @return The downsampled block
     */
    private int[][] downsampleBlock(int[][] block) {
        int originalSize = block.length;
        int newSize = originalSize / 2;
        int[][] downsampledBlock = new int[newSize][newSize];
        
        for (int i = 0; i < newSize; i++) {
            for (int j = 0; j < newSize; j++) {
                int sum = block[2*i][2*j] + block[2*i][2*j+1] + 
                          block[2*i+1][2*j] + block[2*i+1][2*j+1];
                downsampledBlock[i][j] = sum / 4;
            }
        }
        
        return downsampledBlock;
    }
    
    /**
     * Applies geometric transformation (rotation and flip) to a block.
     *
     * @param block The block to transform
     * @param rotation The rotation angle (0, 90, 180, or 270 degrees)
     * @param flip Whether to apply horizontal flip
     * @return The transformed block
     */
    private int[][] applyGeometricTransformation(int[][] block, int rotation, boolean flip) {
        int size = block.length;
        int[][] transformed = new int[size][size];
        
        // Apply rotation
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                switch (rotation) {
                    case 0:
                        transformed[i][j] = block[i][j];
                        break;
                    case 90:
                        transformed[i][j] = block[size-1-j][i];
                        break;
                    case 180:
                        transformed[i][j] = block[size-1-i][size-1-j];
                        break;
                    case 270:
                        transformed[i][j] = block[j][size-1-i];
                        break;
                }
            }
        }
        
        // Apply horizontal flip if needed
        if (flip) {
            int[][] flipped = new int[size][size];
            for (int i = 0; i < size; i++) {
                for (int j = 0; j < size; j++) {
                    flipped[i][j] = transformed[i][size-1-j];
                }
            }
            transformed = flipped;
        }
        
        return transformed;
    }
    
    /**
     * Finds the optimal contrast scaling factor and brightness offset
     * to minimize the error between two blocks.
     *
     * @param rangeBlock The target range block
     * @param domainBlock The domain block to transform
     * @return Array containing [scale, offset]
     */
    private double[] findOptimalParameters(int[][] rangeBlock, int[][] domainBlock) {
        int size = rangeBlock.length;
        int n = size * size;
        
        // Calculate means
        double sumD = 0, sumR = 0, sumD2 = 0, sumDR = 0;
        
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                double d = domainBlock[i][j];
                double r = rangeBlock[i][j];
                
                sumD += d;
                sumR += r;
                sumD2 += d * d;
                sumDR += d * r;
            }
        }
        
        double meanD = sumD / n;
        double meanR = sumR / n;
        
        // Calculate optimal parameters using linear regression
        double numerator = sumDR - (sumD * sumR) / n;
        double denominator = sumD2 - (sumD * sumD) / n;
        
        double scale = 0;
        if (Math.abs(denominator) > 1e-10) {  // Avoid division by zero
            scale = numerator / denominator;
        }
        
        // Cap scale factor to [-1, 1]
        scale = Math.max(-1.0, Math.min(1.0, scale));
        
        double offset = meanR - scale * meanD;
        
        return new double[]{scale, offset};
    }
    
    /**
     * Calculates the Root Mean Squared Error between a range block and a transformed domain block.
     *
     * @param rangeBlock The range block
     * @param domainBlock The domain block
     * @param scale The contrast scaling factor
     * @param offset The brightness offset
     * @return The RMSE value
     */
    private double calculateRMSE(int[][] rangeBlock, int[][] domainBlock, double scale, double offset) {
        int size = rangeBlock.length;
        double sumSquaredError = 0;
        
        for (int i = 0; i < size; i++) {
            for (int j = 0; j < size; j++) {
                double transformedValue = scale * domainBlock[i][j] + offset;
                // Clamp values to [0, 255]
                transformedValue = Math.max(0, Math.min(255, transformedValue));
                
                double error = transformedValue - rangeBlock[i][j];
                sumSquaredError += error * error;
            }
        }
        
        return Math.sqrt(sumSquaredError / (size * size));
    }
}