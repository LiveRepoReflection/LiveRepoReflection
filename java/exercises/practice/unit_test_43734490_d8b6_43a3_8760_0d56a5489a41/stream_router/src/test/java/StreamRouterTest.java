import static org.junit.jupiter.api.Assertions.*;
import org.junit.jupiter.api.Test;
import java.util.*;

class StreamRouterTest {

    @Test
    void testValidAssignmentBasic() {
        int numChannels = 3;
        int channelCapacity = 2000;
        List<Stream> streams = new ArrayList<>();
        streams.add(new Stream(1, 10, 500));
        streams.add(new Stream(2, 5, 800));
        streams.add(new Stream(3, 15, 300));
        streams.add(new Stream(4, 2, 700));
        streams.add(new Stream(5, 8, 600));

        // Call the solve method from StreamRouter
        Map<Integer, Integer> assignment = StreamRouter.solve(numChannels, channelCapacity, streams);

        // Check that returned map is not null
        assertNotNull(assignment);

        // Ensure that each assigned channel is valid and its total dataSize does not exceed channelCapacity
        Map<Integer, Integer> channelDataSize = new HashMap<>();
        for (Stream s : streams) {
            if (assignment.containsKey(s.getStreamId())) {
                int channel = assignment.get(s.getStreamId());
                assertTrue(channel >= 0 && channel < numChannels, "Channel number out of bounds");
                channelDataSize.put(channel, channelDataSize.getOrDefault(channel, 0) + s.getDataSize());
            }
        }
        for (int sum : channelDataSize.values()) {
            assertTrue(sum <= channelCapacity, "Channel capacity exceeded");
        }
    }

    @Test
    void testStreamExceedingChannelCapacity() {
        int numChannels = 2;
        int channelCapacity = 1000;
        List<Stream> streams = new ArrayList<>();
        // This stream's size exceeds channel capacity and should not be assigned.
        streams.add(new Stream(10, 5, 1500));
        // Valid stream
        streams.add(new Stream(11, 8, 500));

        Map<Integer, Integer> assignment = StreamRouter.solve(numChannels, channelCapacity, streams);

        // Stream with id 10 should not be assigned while stream 11 may be assigned.
        assertFalse(assignment.containsKey(10), "Stream exceeding capacity should not be assigned");
        if (assignment.containsKey(11)) {
            int channel = assignment.get(11);
            assertTrue(channel >= 0 && channel < numChannels, "Assigned channel number out of bounds");
        }
    }

    @Test
    void testMultipleStreamsSamePriority() {
        int numChannels = 4;
        int channelCapacity = 2500;
        List<Stream> streams = new ArrayList<>();

        // Create multiple streams with the same priority
        for (int i = 1; i <= 8; i++) {
            streams.add(new Stream(i, 10, 300));
        }

        Map<Integer, Integer> assignment = StreamRouter.solve(numChannels, channelCapacity, streams);
        assertNotNull(assignment);

        // Each assigned stream must be in valid channel
        for (Stream s : streams) {
            if (assignment.containsKey(s.getStreamId())) {
                int channel = assignment.get(s.getStreamId());
                assertTrue(channel >= 0 && channel < numChannels, "Assigned channel number out of bounds");
            }
        }
        
        // Check that the distribution does not overload any channel
        Map<Integer, Integer> channelDataSize = new HashMap<>();
        for (Stream s : streams) {
            if (assignment.containsKey(s.getStreamId())) {
                int channel = assignment.get(s.getStreamId());
                channelDataSize.put(channel, channelDataSize.getOrDefault(channel, 0) + s.getDataSize());
            }
        }
        for (int sum : channelDataSize.values()) {
            assertTrue(sum <= channelCapacity, "Channel capacity exceeded");
        }
    }

    @Test
    void testFairnessInDistribution() {
        int numChannels = 5;
        int channelCapacity = 3000;
        List<Stream> streams = new ArrayList<>();
        
        // Create streams with varying data sizes and priorities
        streams.add(new Stream(21, 1, 1000));
        streams.add(new Stream(22, 2, 800));
        streams.add(new Stream(23, 3, 700));
        streams.add(new Stream(24, 1, 600));
        streams.add(new Stream(25, 2, 500));
        streams.add(new Stream(26, 3, 400));
        streams.add(new Stream(27, 4, 900));
        streams.add(new Stream(28, 0, 300));
        streams.add(new Stream(29, 2, 200));
        streams.add(new Stream(30, 5, 100));

        Map<Integer, Integer> assignment = StreamRouter.solve(numChannels, channelCapacity, streams);
        assertNotNull(assignment);

        Map<Integer, Integer> channelDataSize = new HashMap<>();
        // Initialize channels sum to zero
        for (int i = 0; i < numChannels; i++) {
            channelDataSize.put(i, 0);
        }
        for (Stream s : streams) {
            if (assignment.containsKey(s.getStreamId())) {
                int channel = assignment.get(s.getStreamId());
                channelDataSize.put(channel, channelDataSize.get(channel) + s.getDataSize());
            }
        }
        
        // Check that difference between maximum and minimum load is reasonable.
        int maxLoad = Collections.max(channelDataSize.values());
        int minLoad = Collections.min(channelDataSize.values());
        
        // We expect that the fairness mechanism spreads the load; this threshold is a soft check.
        assertTrue(maxLoad - minLoad <= 1000, "Workload distribution difference is too high");
    }

    @Test
    void testNoValidAssignment() {
        int numChannels = 1;
        int channelCapacity = 500;
        List<Stream> streams = new ArrayList<>();
        // Both streams exceed the capacity when taken together (and only one channel available)
        streams.add(new Stream(31, 2, 400));
        streams.add(new Stream(32, 3, 300));

        Map<Integer, Integer> assignment = StreamRouter.solve(numChannels, channelCapacity, streams);

        // At least one stream may be assigned but not both. 
        // Validate that if a stream is assigned, channel capacity is not exceeded.
        int total = 0;
        for (Stream s : streams) {
            if (assignment.containsKey(s.getStreamId())) {
                total += s.getDataSize();
            }
        }
        assertTrue(total <= channelCapacity, "Assigned streams exceed channel capacity");
    }
}