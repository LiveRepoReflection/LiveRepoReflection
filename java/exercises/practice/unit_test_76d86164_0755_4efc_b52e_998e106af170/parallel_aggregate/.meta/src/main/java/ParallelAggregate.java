import java.io.*;
import java.nio.file.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.logging.*;
import java.util.regex.*;
import java.util.stream.*;

/**
 * Solution to the Parallel Data Processing and Aggregation problem.
 * This implementation uses a distributed approach with multiple stages:
 * 1. Split and preprocess input data across available machines
 * 2. Partition the data using consistent hashing to distribute keys evenly
 * 3. Perform local aggregation on each machine
 * 4. Merge the results and sort alphabetically
 */
public class ParallelAggregate {
    private static final Logger LOGGER = Logger.getLogger(ParallelAggregate.class.getName());
    private static final Pattern KEY_VALUE_PATTERN = Pattern.compile("^([^,]+),([-+]?[0-9]*\\.?[0-9]+(?:[eE][-+]?[0-9]+)?)$");
    private ExecutorService executorService;
    private int machineCount;
    private int memoryLimitMB;
    
    /**
     * Process the input files and aggregate the key-value pairs.
     * 
     * @param inputFilePaths List of input file paths
     * @param outputFilePath Path to the output file
     * @param machineCount Number of machines available
     * @param memoryLimitMB Memory limit per machine in MB
     * @throws IOException If there is an error reading or writing files
     */
    public void process(List<String> inputFilePaths, String outputFilePath, int machineCount, int memoryLimitMB) throws IOException {
        this.machineCount = machineCount;
        this.memoryLimitMB = memoryLimitMB;
        
        // Initialize thread pool for parallel processing
        executorService = Executors.newFixedThreadPool(machineCount);
        
        try {
            if (inputFilePaths.isEmpty()) {
                // Handle empty input case
                Files.write(Paths.get(outputFilePath), new ArrayList<String>());
                return;
            }
            
            // Step 1: Create temporary directories for intermediate files
            Path tempDir = Files.createTempDirectory("parallel_aggregate_");
            Path partitionsDir = Files.createDirectory(tempDir.resolve("partitions"));
            Path aggregatedDir = Files.createDirectory(tempDir.resolve("aggregated"));
            
            // Step 2: Split and partition input files
            partitionInputFiles(inputFilePaths, partitionsDir);
            
            // Step 3: Process partitions in parallel
            processPartitions(partitionsDir, aggregatedDir);
            
            // Step 4: Merge aggregated results
            mergeResults(aggregatedDir, outputFilePath);
            
            // Clean up temporary files
            deleteDirectory(tempDir);
            
        } catch (Exception e) {
            LOGGER.log(Level.SEVERE, "Error processing data", e);
            throw new RuntimeException("Failed to process data", e);
        } finally {
            executorService.shutdown();
            try {
                if (!executorService.awaitTermination(60, TimeUnit.SECONDS)) {
                    executorService.shutdownNow();
                }
            } catch (InterruptedException e) {
                executorService.shutdownNow();
            }
        }
    }
    
    /**
     * Split input files and partition them based on key hash
     */
    private void partitionInputFiles(List<String> inputFilePaths, Path partitionsDir) throws IOException, InterruptedException, ExecutionException {
        // Create partition writers
        BufferedWriter[] partitionWriters = new BufferedWriter[machineCount];
        for (int i = 0; i < machineCount; i++) {
            partitionWriters[i] = Files.newBufferedWriter(partitionsDir.resolve("partition_" + i + ".txt"));
        }
        
        // Calculate approximate lines per batch based on memory limit
        // Assuming average line size is 50 bytes
        int approximateLinesPerBatch = (memoryLimitMB * 1024 * 1024) / (50 * machineCount);
        
        // Define threshold to flush partitions (80% of memory limit)
        int flushThreshold = (int) (approximateLinesPerBatch * 0.8);
        int[] lineCounters = new int[machineCount];
        
        // Process each input file
        for (String inputFilePath : inputFilePaths) {
            try (BufferedReader reader = Files.newBufferedReader(Paths.get(inputFilePath))) {
                String line;
                while ((line = reader.readLine()) != null) {
                    // Parse and validate the line
                    Matcher matcher = KEY_VALUE_PATTERN.matcher(line);
                    if (!matcher.matches()) {
                        LOGGER.warning("Malformed line: " + line);
                        continue;
                    }
                    
                    String key = matcher.group(1);
                    
                    // Determine partition using consistent hashing
                    int partition = Math.abs(key.hashCode() % machineCount);
                    
                    // Write to appropriate partition
                    partitionWriters[partition].write(line);
                    partitionWriters[partition].newLine();
                    
                    // Increment line counter for this partition
                    lineCounters[partition]++;
                    
                    // If we've reached the flush threshold, flush the writer
                    if (lineCounters[partition] >= flushThreshold) {
                        partitionWriters[partition].flush();
                        lineCounters[partition] = 0;
                    }
                }
            }
        }
        
        // Close all partition writers
        for (BufferedWriter writer : partitionWriters) {
            writer.close();
        }
    }
    
    /**
     * Process each partition in parallel on separate machines
     */
    private void processPartitions(Path partitionsDir, Path aggregatedDir) throws IOException, InterruptedException, ExecutionException {
        List<Future<Void>> futures = new ArrayList<>();
        
        // Process each partition in parallel
        for (int i = 0; i < machineCount; i++) {
            final int machineId = i;
            futures.add(executorService.submit(() -> {
                Path partitionPath = partitionsDir.resolve("partition_" + machineId + ".txt");
                Path aggregatedPath = aggregatedDir.resolve("aggregated_" + machineId + ".txt");
                
                // Skip if partition file doesn't exist or is empty
                if (!Files.exists(partitionPath) || Files.size(partitionPath) == 0) {
                    Files.createFile(aggregatedPath);
                    return null;
                }
                
                // Process the partition with limited memory
                processPartitionWithLimitedMemory(partitionPath, aggregatedPath);
                return null;
            }));
        }
        
        // Wait for all tasks to complete
        for (Future<Void> future : futures) {
            future.get();
        }
    }
    
    /**
     * Process a single partition with limited memory using external sorting and aggregation
     */
    private void processPartitionWithLimitedMemory(Path partitionPath, Path aggregatedPath) throws IOException {
        // Approximate number of entries that can fit in memory
        // Assuming each entry takes about 100 bytes in a HashMap
        int maxInMemoryEntries = (memoryLimitMB * 1024 * 1024) / 100;
        
        // Create temporary directories for sorted chunks and merged results
        Path tempChunksDir = Files.createTempDirectory("chunks_");
        
        try {
            // Step 1: Sort and aggregate data in chunks
            List<Path> sortedChunkPaths = sortAndAggregateInChunks(partitionPath, tempChunksDir, maxInMemoryEntries);
            
            // Step 2: Merge sorted chunks
            if (sortedChunkPaths.size() == 1) {
                // Only one chunk, just move it to the aggregated path
                Files.move(sortedChunkPaths.get(0), aggregatedPath, StandardCopyOption.REPLACE_EXISTING);
            } else {
                // Merge multiple chunks using a priority queue
                mergeSortedChunks(sortedChunkPaths, aggregatedPath);
            }
        } finally {
            // Clean up temporary files
            deleteDirectory(tempChunksDir);
        }
    }
    
    /**
     * Sort and aggregate data in chunks that fit in memory
     */
    private List<Path> sortAndAggregateInChunks(Path partitionPath, Path chunksDir, int maxInMemoryEntries) throws IOException {
        List<Path> chunkPaths = new ArrayList<>();
        int chunkCounter = 0;
        
        try (BufferedReader reader = Files.newBufferedReader(partitionPath)) {
            Map<String, Double> aggregationMap = new HashMap<>();
            String line;
            
            while ((line = reader.readLine()) != null) {
                Matcher matcher = KEY_VALUE_PATTERN.matcher(line);
                if (!matcher.matches()) {
                    continue;  // Skip malformed lines
                }
                
                String key = matcher.group(1);
                double value = Double.parseDouble(matcher.group(2));
                
                // Add or update value in map
                aggregationMap.merge(key, value, Double::sum);
                
                // If we've reached the memory limit, write out the chunk
                if (aggregationMap.size() >= maxInMemoryEntries) {
                    Path chunkPath = chunksDir.resolve("chunk_" + chunkCounter++ + ".txt");
                    writeAggregatedChunk(aggregationMap, chunkPath);
                    chunkPaths.add(chunkPath);
                    aggregationMap.clear();
                }
            }
            
            // Write the last chunk if there's any data left
            if (!aggregationMap.isEmpty()) {
                Path chunkPath = chunksDir.resolve("chunk_" + chunkCounter++ + ".txt");
                writeAggregatedChunk(aggregationMap, chunkPath);
                chunkPaths.add(chunkPath);
            }
        }
        
        return chunkPaths;
    }
    
    /**
     * Write aggregated data from a map to a file, sorted by key
     */
    private void writeAggregatedChunk(Map<String, Double> aggregationMap, Path chunkPath) throws IOException {
        try (BufferedWriter writer = Files.newBufferedWriter(chunkPath)) {
            // Sort entries by key
            List<Map.Entry<String, Double>> sortedEntries = new ArrayList<>(aggregationMap.entrySet());
            sortedEntries.sort(Map.Entry.comparingByKey());
            
            // Write sorted entries
            for (Map.Entry<String, Double> entry : sortedEntries) {
                writer.write(entry.getKey() + "," + entry.getValue());
                writer.newLine();
            }
        }
    }
    
    /**
     * Merge multiple sorted chunks using a priority queue
     */
    private void mergeSortedChunks(List<Path> chunkPaths, Path outputPath) throws IOException {
        // Create readers for each chunk
        List<BufferedReader> readers = new ArrayList<>();
        for (Path chunkPath : chunkPaths) {
            readers.add(Files.newBufferedReader(chunkPath));
        }
        
        // Create a priority queue to merge chunks
        PriorityQueue<ChunkEntry> priorityQueue = new PriorityQueue<>();
        
        // Initialize the queue with the first entry from each chunk
        for (int i = 0; i < readers.size(); i++) {
            String line = readers.get(i).readLine();
            if (line != null) {
                String[] parts = line.split(",", 2);
                priorityQueue.add(new ChunkEntry(parts[0], Double.parseDouble(parts[1]), i));
            }
        }
        
        try (BufferedWriter writer = Files.newBufferedWriter(outputPath)) {
            String currentKey = null;
            double currentSum = 0.0;
            
            // Process entries in order
            while (!priorityQueue.isEmpty()) {
                ChunkEntry entry = priorityQueue.poll();
                
                // If this is a new key, write the previous key's aggregated value
                if (currentKey != null && !currentKey.equals(entry.key)) {
                    writer.write(currentKey + "," + currentSum);
                    writer.newLine();
                    currentSum = entry.value;
                } else {
                    // Aggregate values for the same key
                    currentSum += entry.value;
                }
                
                currentKey = entry.key;
                
                // Read the next entry from the same chunk
                String nextLine = readers.get(entry.chunkIndex).readLine();
                if (nextLine != null) {
                    String[] parts = nextLine.split(",", 2);
                    priorityQueue.add(new ChunkEntry(parts[0], Double.parseDouble(parts[1]), entry.chunkIndex));
                }
            }
            
            // Write the last entry
            if (currentKey != null) {
                writer.write(currentKey + "," + currentSum);
                writer.newLine();
            }
        } finally {
            // Close all readers
            for (BufferedReader reader : readers) {
                reader.close();
            }
        }
    }
    
    /**
     * Merge all aggregated results from different machines
     */
    private void mergeResults(Path aggregatedDir, String outputFilePath) throws IOException {
        List<Path> aggregatedPaths = Files.list(aggregatedDir).collect(Collectors.toList());
        
        // If no aggregated files or all are empty, create an empty output file
        if (aggregatedPaths.isEmpty()) {
            Files.write(Paths.get(outputFilePath), new ArrayList<String>());
            return;
        }
        
        // Merge all aggregated files
        mergeSortedChunks(aggregatedPaths, Paths.get(outputFilePath));
    }
    
    /**
     * Recursive method to delete a directory and all its contents
     */
    private void deleteDirectory(Path directory) throws IOException {
        if (Files.exists(directory)) {
            Files.walk(directory)
                .sorted(Comparator.reverseOrder())
                .forEach(path -> {
                    try {
                        Files.delete(path);
                    } catch (IOException e) {
                        LOGGER.log(Level.WARNING, "Failed to delete: " + path, e);
                    }
                });
        }
    }
    
    /**
     * Helper class to represent entries in the priority queue during merge
     */
    private static class ChunkEntry implements Comparable<ChunkEntry> {
        String key;
        double value;
        int chunkIndex;
        
        ChunkEntry(String key, double value, int chunkIndex) {
            this.key = key;
            this.value = value;
            this.chunkIndex = chunkIndex;
        }
        
        @Override
        public int compareTo(ChunkEntry other) {
            return this.key.compareTo(other.key);
        }
    }
}