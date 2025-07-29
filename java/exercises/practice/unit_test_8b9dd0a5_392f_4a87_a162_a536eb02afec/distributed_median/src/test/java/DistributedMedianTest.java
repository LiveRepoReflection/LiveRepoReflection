import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.Timeout;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class DistributedMedianTest {

    /**
     * Utility method to compute the median of a sorted list.
     */
    private double computeMedian(List<Integer> sortedList) {
        int n = sortedList.size();
        if (n % 2 == 1) {
            return sortedList.get(n / 2);
        } else {
            return (sortedList.get(n / 2 - 1) + sortedList.get(n / 2)) / 2.0;
        }
    }

    /**
     * Test single-threaded median computation.
     */
    @Test
    public void testSingleThreadMedian() {
        MedianCalculator medianCalc = new MedianCalculator();
        int[] numbers = {1, 3, 2, 5, 4};
        List<Integer> addedNumbers = new ArrayList<>();
        for (int num : numbers) {
            medianCalc.add(num);
            addedNumbers.add(num);
        }
        Collections.sort(addedNumbers);
        double expectedMedian = computeMedian(addedNumbers);
        assertEquals(expectedMedian, medianCalc.getMedian(), "Median should be calculated correctly in single thread");
    }

    /**
     * Test single-threaded even count median computation.
     */
    @Test
    public void testEvenCountMedian() {
        MedianCalculator medianCalc = new MedianCalculator();
        int[] numbers = {10, 20, 30, 40};
        List<Integer> addedNumbers = new ArrayList<>();
        for (int num : numbers) {
            medianCalc.add(num);
            addedNumbers.add(num);
        }
        Collections.sort(addedNumbers);
        double expectedMedian = computeMedian(addedNumbers);
        assertEquals(expectedMedian, medianCalc.getMedian(), "Median for even count should be average of two middle numbers");
    }

    /**
     * Test concurrent updates from multiple threads.
     */
    @Test
    @Timeout(value = 10, unit = TimeUnit.SECONDS)
    public void testConcurrentUpdates() throws InterruptedException, ExecutionException {
        final int threadCount = 10;
        final int numbersPerThread = 1000;
        final ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        final MedianCalculator medianCalc = new MedianCalculator();
        final List<Integer> allNumbers = Collections.synchronizedList(new ArrayList<>());

        List<Callable<Void>> tasks = new ArrayList<>();
        for (int i = 0; i < threadCount; i++) {
            tasks.add(() -> {
                Random rand = new Random();
                for (int j = 0; j < numbersPerThread; j++) {
                    int num = rand.nextInt(10000) - 5000; // range -5000 to 4999
                    medianCalc.add(num);
                    allNumbers.add(num);
                }
                return null;
            });
        }

        List<Future<Void>> futures = executor.invokeAll(tasks);
        for (Future<Void> f : futures) {
            f.get();
        }
        executor.shutdown();
        executor.awaitTermination(5, TimeUnit.SECONDS);

        List<Integer> sortedNumbers = new ArrayList<>(allNumbers);
        Collections.sort(sortedNumbers);
        double expectedMedian = computeMedian(sortedNumbers);
        double actualMedian = medianCalc.getMedian();
        assertEquals(expectedMedian, actualMedian, "Concurrent updates should result in correct median");
    }

    /**
     * Test concurrent updates with induced delays to simulate out-of-order and delayed arrivals.
     */
    @Test
    @Timeout(value = 15, unit = TimeUnit.SECONDS)
    public void testOutOfOrderUpdates() throws InterruptedException, ExecutionException {
        final int threadCount = 20;
        final int numbersPerThread = 500;
        final ExecutorService executor = Executors.newFixedThreadPool(threadCount);
        final MedianCalculator medianCalc = new MedianCalculator();
        final List<Integer> allNumbers = Collections.synchronizedList(new ArrayList<>());

        List<Callable<Void>> tasks = new ArrayList<>();
        for (int i = 0; i < threadCount; i++) {
            tasks.add(() -> {
                Random rand = new Random();
                for (int j = 0; j < numbersPerThread; j++) {
                    // Introduce random sleep to simulate network delay or out-of-order arrival.
                    Thread.sleep(rand.nextInt(5));
                    int num = rand.nextInt(20000) - 10000; // range -10000 to 9999
                    medianCalc.add(num);
                    allNumbers.add(num);
                }
                return null;
            });
        }

        List<Future<Void>> futures = executor.invokeAll(tasks);
        for (Future<Void> f : futures) {
            f.get();
        }
        executor.shutdown();
        executor.awaitTermination(10, TimeUnit.SECONDS);

        List<Integer> sortedNumbers = new ArrayList<>(allNumbers);
        Collections.sort(sortedNumbers);
        double expectedMedian = computeMedian(sortedNumbers);
        double actualMedian = medianCalc.getMedian();
        assertEquals(expectedMedian, actualMedian, "Out-of-order updates should result in correct median");
    }
    
    /**
     * Test multiple sequential getMedian calls during continuous addition.
     */
    @Test
    public void testSequentialGetMedianDuringUpdates() {
        MedianCalculator medianCalc = new MedianCalculator();
        List<Integer> addedNumbers = new ArrayList<>();
        for (int i = 0; i < 1000; i++) {
            int num = (i % 100) - 50; // Create a repeating pattern
            medianCalc.add(num);
            addedNumbers.add(num);
            if ((i + 1) % 100 == 0) {
                List<Integer> tempList = new ArrayList<>(addedNumbers);
                Collections.sort(tempList);
                double expectedMedian = computeMedian(tempList);
                double actualMedian = medianCalc.getMedian();
                assertTrue(Math.abs(expectedMedian - actualMedian) < 1e-6, 
                    "Median should be updated correctly during sequential adds");
            }
        }
    }
}