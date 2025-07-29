import java.util.PriorityQueue;

public class MedianCalculator {

    // Max-heap for lower half of numbers.
    private final PriorityQueue<Integer> lowerHalf;
    // Min-heap for upper half of numbers.
    private final PriorityQueue<Integer> upperHalf;

    public MedianCalculator() {
        // For the lower half, we use reversed order to simulate a max heap.
        lowerHalf = new PriorityQueue<>((a, b) -> Integer.compare(b, a));
        // Min-heap for the upper half.
        upperHalf = new PriorityQueue<>();
    }

    // Synchronized add method to guarantee thread safety.
    public synchronized void add(int num) {
        if (lowerHalf.isEmpty() || num <= lowerHalf.peek()) {
            lowerHalf.offer(num);
        } else {
            upperHalf.offer(num);
        }
        rebalanceHeaps();
    }

    // Synchronized getMedian method to guarantee thread safety.
    public synchronized double getMedian() {
        if (lowerHalf.isEmpty() && upperHalf.isEmpty()) {
            return 0.0;
        }
        if (lowerHalf.size() == upperHalf.size()) {
            // Even number of elements: median is the average of two middle values.
            return (lowerHalf.peek() + upperHalf.peek()) / 2.0;
        } else {
            // Lower half always has one extra element after rebalancing.
            return lowerHalf.peek();
        }
    }

    // Helper method to rebalance the two heaps.
    private void rebalanceHeaps() {
        // Ensure that the sizes of the two heaps do not differ by more than 1.
        if (lowerHalf.size() > upperHalf.size() + 1) {
            upperHalf.offer(lowerHalf.poll());
        } else if (upperHalf.size() > lowerHalf.size()) {
            lowerHalf.offer(upperHalf.poll());
        }
    }
}