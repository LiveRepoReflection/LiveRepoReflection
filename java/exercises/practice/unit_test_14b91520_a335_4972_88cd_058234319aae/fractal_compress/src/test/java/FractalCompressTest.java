import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Random;

public class FractalCompressTest {
    
    private FractalCompressor compressor;
    
    @BeforeEach
    void setUp() {
        compressor = new FractalCompressor();
    }
    
    @Nested
    @DisplayName("Basic Tests")
    class BasicTests {
        
        @Test
        @DisplayName("Test with a 4x4 image, R=2, S=2")
        void testSimple4x4Image() {
            int[][] image = {
                {100, 110, 120, 130},
                {105, 115, 125, 135},
                {110, 120, 130, 140},
                {115, 125, 135, 145}
            };
            int rangeSize = 2;
            int stride = 2;
            
            List<Transformation> transformations = compressor.compress(image, rangeSize, stride);
            
            // Check correct number of transformations
            assertEquals(4, transformations.size(), "There should be 4 transformations for a 4x4 image with rangeSize=2");
            
            // Check each transformation has valid parameters
            for (Transformation t : transformations) {
                // Valid range coordinates
                assertTrue(t.rangeRow >= 0 && t.rangeRow < image.length, "Range row is invalid");
                assertTrue(t.rangeCol >= 0 && t.rangeCol < image[0].length, "Range col is invalid");
                
                // Valid domain coordinates
                assertTrue(t.domainRow >= 0 && t.domainRow <= image.length - 2*rangeSize, "Domain row is invalid");
                assertTrue(t.domainCol >= 0 && t.domainCol <= image[0].length - 2*rangeSize, "Domain col is invalid");
                
                // Valid rotation
                assertTrue(t.rotation == 0 || t.rotation == 90 || t.rotation == 180 || t.rotation == 270, 
                           "Rotation must be 0, 90, 180, or 270");
                
                // Valid scale factor
                assertTrue(t.scale >= -1.0 && t.scale <= 1.0, "Scale factor must be between -1.0 and 1.0");
            }
            
            // Verify no duplicate range blocks
            for (int i = 0; i < transformations.size(); i++) {
                Transformation t1 = transformations.get(i);
                for (int j = i + 1; j < transformations.size(); j++) {
                    Transformation t2 = transformations.get(j);
                    assertFalse(t1.rangeRow == t2.rangeRow && t1.rangeCol == t2.rangeCol,
                               "Duplicate range blocks found");
                }
            }
        }
        
        @Test
        @DisplayName("Test with a 2x2 image, R=1, S=1")
        void testMinimalImage() {
            int[][] image = {
                {100, 150},
                {200, 250}
            };
            int rangeSize = 1;
            int stride = 1;
            
            List<Transformation> transformations = compressor.compress(image, rangeSize, stride);
            
            assertEquals(4, transformations.size(), "There should be 4 transformations for a 2x2 image with rangeSize=1");
        }
    }
    
    @Nested
    @DisplayName("Edge Cases")
    class EdgeCases {
        
        @Test
        @DisplayName("Test with empty image")
        void testEmptyImage() {
            int[][] image = {};
            int rangeSize = 1;
            int stride = 1;
            
            assertThrows(IllegalArgumentException.class, () -> {
                compressor.compress(image, rangeSize, stride);
            }, "Should throw IllegalArgumentException for empty image");
        }
        
        @Test
        @DisplayName("Test with invalid range size")
        void testInvalidRangeSize() {
            int[][] image = {
                {100, 150},
                {200, 250}
            };
            int rangeSize = 3; // Larger than half the image size
            int stride = 1;
            
            assertThrows(IllegalArgumentException.class, () -> {
                compressor.compress(image, rangeSize, stride);
            }, "Should throw IllegalArgumentException for invalid range size");
        }
        
        @Test
        @DisplayName("Test with invalid stride")
        void testInvalidStride() {
            int[][] image = {
                {100, 150},
                {200, 250}
            };
            int rangeSize = 1;
            int stride = 0; // Invalid stride
            
            assertThrows(IllegalArgumentException.class, () -> {
                compressor.compress(image, rangeSize, stride);
            }, "Should throw IllegalArgumentException for invalid stride");
        }
        
        @Test
        @DisplayName("Test with non-power-of-2 image dimensions")
        void testNonPowerOf2Dimensions() {
            int[][] image = {
                {100, 150, 200},
                {200, 250, 300}
            };
            int rangeSize = 1;
            int stride = 1;
            
            assertThrows(IllegalArgumentException.class, () -> {
                compressor.compress(image, rangeSize, stride);
            }, "Should throw IllegalArgumentException for non-power-of-2 dimensions");
        }
        
        @Test
        @DisplayName("Test with non-power-of-2 range size")
        void testNonPowerOf2RangeSize() {
            int[][] image = {
                {100, 150, 200, 250},
                {200, 250, 300, 350},
                {300, 350, 400, 450},
                {350, 400, 450, 500}
            };
            int rangeSize = 3; // Not a power of 2
            int stride = 1;
            
            assertThrows(IllegalArgumentException.class, () -> {
                compressor.compress(image, rangeSize, stride);
            }, "Should throw IllegalArgumentException for non-power-of-2 range size");
        }
    }
    
    @Nested
    @DisplayName("Comprehensive Tests")
    class ComprehensiveTests {
        
        @Test
        @DisplayName("Test with a larger 8x8 image")
        void testLargerImage() {
            int[][] image = new int[8][8];
            // Fill with gradient pattern
            for (int i = 0; i < 8; i++) {
                for (int j = 0; j < 8; j++) {
                    image[i][j] = (i * 32) + j * 4;
                }
            }
            
            int rangeSize = 2;
            int stride = 2;
            
            List<Transformation> transformations = compressor.compress(image, rangeSize, stride);
            
            assertEquals(16, transformations.size(), "There should be 16 transformations for an 8x8 image with rangeSize=2");
            
            // Check coverage of all range blocks
            boolean[][] covered = new boolean[8][8];
            for (Transformation t : transformations) {
                for (int i = 0; i < rangeSize; i++) {
                    for (int j = 0; j < rangeSize; j++) {
                        int row = t.rangeRow + i;
                        int col = t.rangeCol + j;
                        assertFalse(covered[row][col], "Range pixel already covered");
                        covered[row][col] = true;
                    }
                }
            }
            
            // Ensure all pixels are covered
            for (int i = 0; i < 8; i++) {
                for (int j = 0; j < 8; j++) {
                    assertTrue(covered[i][j], "Pixel at (" + i + "," + j + ") not covered");
                }
            }
        }
        
        @Test
        @DisplayName("Test with random image data")
        void testRandomImage() {
            Random random = new Random(42); // Fixed seed for reproducibility
            int size = 16;
            int[][] image = new int[size][size];
            
            // Fill with random values
            for (int i = 0; i < size; i++) {
                for (int j = 0; j < size; j++) {
                    image[i][j] = random.nextInt(256);
                }
            }
            
            int rangeSize = 4;
            int stride = 2;
            
            List<Transformation> transformations = compressor.compress(image, rangeSize, stride);
            
            assertEquals(16, transformations.size(), 
                        "There should be 16 transformations for a 16x16 image with rangeSize=4");
        }
        
        @Test
        @DisplayName("Test with uniform image")
        void testUniformImage() {
            int[][] image = new int[4][4];
            // Fill with constant value
            for (int i = 0; i < 4; i++) {
                for (int j = 0; j < 4; j++) {
                    image[i][j] = 128;
                }
            }
            
            int rangeSize = 2;
            int stride = 2;
            
            List<Transformation> transformations = compressor.compress(image, rangeSize, stride);
            
            assertEquals(4, transformations.size(), 
                        "There should be 4 transformations for a 4x4 image with rangeSize=2");
            
            // For uniform image, scale should be close to 0 and offset close to 128
            for (Transformation t : transformations) {
                assertTrue(Math.abs(t.scale) < 0.1, "Scale should be close to 0 for uniform image");
                assertTrue(Math.abs(t.offset - 128) < 0.1, "Offset should be close to 128 for uniform image");
            }
        }
        
        @Test
        @DisplayName("Test with vertical gradient image")
        void testVerticalGradientImage() {
            int[][] image = new int[8][8];
            // Fill with vertical gradient
            for (int i = 0; i < 8; i++) {
                for (int j = 0; j < 8; j++) {
                    image[i][j] = i * 32; // 0 to 224 in steps of 32
                }
            }
            
            int rangeSize = 2;
            int stride = 2;
            
            List<Transformation> transformations = compressor.compress(image, rangeSize, stride);
            
            assertEquals(16, transformations.size(), 
                        "There should be 16 transformations for an 8x8 image with rangeSize=2");
        }
        
        @Test
        @DisplayName("Test with horizontal gradient image")
        void testHorizontalGradientImage() {
            int[][] image = new int[8][8];
            // Fill with horizontal gradient
            for (int i = 0; i < 8; i++) {
                for (int j = 0; j < 8; j++) {
                    image[i][j] = j * 32; // 0 to 224 in steps of 32
                }
            }
            
            int rangeSize = 2;
            int stride = 2;
            
            List<Transformation> transformations = compressor.compress(image, rangeSize, stride);
            
            assertEquals(16, transformations.size(), 
                        "There should be 16 transformations for an 8x8 image with rangeSize=2");
        }
    }
    
    @Nested
    @DisplayName("Performance Tests")
    class PerformanceTests {
        
        @Test
        @DisplayName("Test performance with larger image")
        void testLargeImagePerformance() {
            int size = 128;
            int[][] image = new int[size][size];
            Random random = new Random(42);
            
            // Fill with random values
            for (int i = 0; i < size; i++) {
                for (int j = 0; j < size; j++) {
                    image[i][j] = random.nextInt(256);
                }
            }
            
            int rangeSize = 8;
            int stride = 4;
            
            long startTime = System.currentTimeMillis();
            List<Transformation> transformations = compressor.compress(image, rangeSize, stride);
            long endTime = System.currentTimeMillis();
            
            long executionTime = endTime - startTime;
            System.out.println("Execution time for 128x128 image: " + executionTime + " ms");
            
            // Check correct number of transformations
            int expectedTransformations = (size / rangeSize) * (size / rangeSize);
            assertEquals(expectedTransformations, transformations.size(), 
                        "There should be " + expectedTransformations + " transformations");
            
            // We're not setting a hard time limit, but logging the time for review
            assertTrue(executionTime < 30000, "Execution time should be reasonable (< 30 seconds)");
        }
    }
}