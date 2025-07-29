import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;
import org.junit.jupiter.api.io.TempDir;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Random;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;

public class ParallelAggregateTest {

    private ParallelAggregate aggregator;
    
    @TempDir
    Path tempDir;
    
    @BeforeEach
    public void setup() {
        aggregator = new ParallelAggregate();
    }

    @Test
    public void testBasicAggregation() throws Exception {
        // Create test input files
        List<String> inputFiles = createInputFiles(
            List.of(
                "apple,1.0",
                "banana,2.5",
                "apple,3.5"
            ),
            List.of(
                "cherry,4.0",
                "banana,1.5",
                "date,2.0"
            )
        );

        String outputFile = tempDir.resolve("output.txt").toString();
        
        // Process with 2 machines, 10MB memory limit
        aggregator.process(inputFiles, outputFile, 2, 10);
        
        // Verify output
        List<String> output = Files.readAllLines(Path.of(outputFile));
        assertEquals(4, output.size());
        assertEquals("apple,4.5", output.get(0));
        assertEquals("banana,4.0", output.get(1));
        assertEquals("cherry,4.0", output.get(2));
        assertEquals("date,2.0", output.get(3));
    }
    
    @Test
    public void testLargeNumberOfUniqueKeys() throws Exception {
        // Create many unique keys
        List<String> data1 = generateUniqueKeyValuePairs(1000, 1);
        List<String> data2 = generateUniqueKeyValuePairs(1000, 1001);
        
        List<String> inputFiles = createInputFiles(data1, data2);
        String outputFile = tempDir.resolve("output_large.txt").toString();
        
        // Process with 2 machines, 10MB memory limit
        aggregator.process(inputFiles, outputFile, 2, 10);
        
        // Verify output
        List<String> output = Files.readAllLines(Path.of(outputFile));
        assertEquals(2000, output.size());
    }
    
    @Test
    @Timeout(value = 5, unit = TimeUnit.SECONDS)
    public void testPerformanceWithLargeData() throws Exception {
        // Create large dataset with repeated keys
        List<String> data1 = generateRandomKeyValuePairs(10000, 100);
        List<String> data2 = generateRandomKeyValuePairs(10000, 100);
        
        List<String> inputFiles = createInputFiles(data1, data2);
        String outputFile = tempDir.resolve("output_perf.txt").toString();
        
        // Process with 4 machines, limited memory
        long startTime = System.currentTimeMillis();
        aggregator.process(inputFiles, outputFile, 4, 5);
        long endTime = System.currentTimeMillis();
        
        // Verify output
        List<String> output = Files.readAllLines(Path.of(outputFile));
        assertTrue(output.size() > 0 && output.size() <= 100);
        
        System.out.println("Performance test completed in " + (endTime - startTime) + "ms");
    }
    
    @Test
    public void testMalformedData() throws Exception {
        // Create test input files with some malformed data
        List<String> inputFiles = createInputFiles(
            List.of(
                "apple,1.0",
                "invalid_line",
                "banana,2.5",
                "missing_value,"
            ),
            List.of(
                "cherry,4.0",
                "not_a_double,xyz",
                "banana,1.5"
            )
        );

        String outputFile = tempDir.resolve("output_malformed.txt").toString();
        
        // Process with 2 machines, 10MB memory limit
        aggregator.process(inputFiles, outputFile, 2, 10);
        
        // Verify output - should only contain valid entries
        List<String> output = Files.readAllLines(Path.of(outputFile));
        assertEquals(3, output.size());
        assertEquals("apple,1.0", output.get(0));
        assertEquals("banana,4.0", output.get(1));
        assertEquals("cherry,4.0", output.get(2));
    }
    
    @Test
    public void testNumericalStability() throws Exception {
        // Create data with very small and very large numbers
        List<String> inputFiles = createInputFiles(
            List.of(
                "key1,1e-10",
                "key1,1e-10",
                "key1,1e-10",
                "key1,1e10"
            ),
            List.of(
                "key2,1e-10",
                "key2,-1e10",
                "key2,1e-10"
            )
        );

        String outputFile = tempDir.resolve("output_numerical.txt").toString();
        
        // Process with 2 machines, 10MB memory limit
        aggregator.process(inputFiles, outputFile, 2, 10);
        
        // Verify output - check numerical stability
        List<String> output = Files.readAllLines(Path.of(outputFile));
        assertEquals(2, output.size());
        
        // Parse the results to verify the numerical values
        String[] key1Parts = output.get(0).split(",");
        String[] key2Parts = output.get(1).split(",");
        
        assertEquals("key1", key1Parts[0]);
        assertEquals("key2", key2Parts[0]);
        
        double key1Value = Double.parseDouble(key1Parts[1]);
        double key2Value = Double.parseDouble(key2Parts[1]);
        
        assertEquals(1e10 + 3e-10, key1Value, 1e-9);
        assertEquals(-1e10 + 2e-10, key2Value, 1e-9);
    }

    @Test
    public void testEmptyInput() throws Exception {
        List<String> inputFiles = createInputFiles(List.of(), List.of());
        String outputFile = tempDir.resolve("output_empty.txt").toString();
        
        aggregator.process(inputFiles, outputFile, 2, 10);
        
        List<String> output = Files.readAllLines(Path.of(outputFile));
        assertEquals(0, output.size());
    }
    
    @Test
    public void testSingleMachine() throws Exception {
        // Create test input files
        List<String> inputFiles = createInputFiles(
            List.of("apple,1.0", "banana,2.5"),
            List.of("cherry,4.0", "banana,1.5")
        );

        String outputFile = tempDir.resolve("output_single.txt").toString();
        
        // Process with 1 machine
        aggregator.process(inputFiles, outputFile, 1, 10);
        
        // Verify output
        List<String> output = Files.readAllLines(Path.of(outputFile));
        assertEquals(3, output.size());
        assertEquals("apple,1.0", output.get(0));
        assertEquals("banana,4.0", output.get(1));
        assertEquals("cherry,4.0", output.get(2));
    }
    
    @Test
    public void testVeryLowMemoryLimit() throws Exception {
        // Create test input files
        List<String> inputFiles = createInputFiles(
            List.of("apple,1.0", "banana,2.5"),
            List.of("cherry,4.0", "banana,1.5")
        );

        String outputFile = tempDir.resolve("output_low_mem.txt").toString();
        
        // Process with very limited memory
        aggregator.process(inputFiles, outputFile, 2, 1);
        
        // Verify output
        List<String> output = Files.readAllLines(Path.of(outputFile));
        assertEquals(3, output.size());
    }
    
    // Helper methods to create test data
    
    private List<String> createInputFiles(List<String> data1, List<String> data2) throws IOException {
        File file1 = tempDir.resolve("input1.txt").toFile();
        File file2 = tempDir.resolve("input2.txt").toFile();
        
        writeToFile(file1, data1);
        writeToFile(file2, data2);
        
        return Arrays.asList(file1.getAbsolutePath(), file2.getAbsolutePath());
    }
    
    private void writeToFile(File file, List<String> lines) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(file))) {
            for (String line : lines) {
                writer.write(line);
                writer.newLine();
            }
        }
    }
    
    private List<String> generateUniqueKeyValuePairs(int count, int startIndex) {
        return new Random().doubles(count, 1.0, 100.0)
                .mapToObj(value -> "key" + (startIndex + value) + "," + value)
                .collect(Collectors.toList());
    }
    
    private List<String> generateRandomKeyValuePairs(int count, int uniqueKeyCount) {
        Random rand = new Random();
        return rand.doubles(count, 1.0, 100.0)
                .mapToObj(value -> {
                    int keyIndex = rand.nextInt(uniqueKeyCount);
                    return "key" + keyIndex + "," + value;
                })
                .collect(Collectors.toList());
    }
}