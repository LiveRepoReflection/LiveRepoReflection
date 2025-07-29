import java.util.*;

public class StreamRouter {

    public static Map<Integer, Integer> solve(int numChannels, int channelCapacity, List<Stream> streams) {
        // Map to store final assignment: streamId -> channel number.
        Map<Integer, Integer> assignment = new HashMap<>();

        // Create channel state: for each channel index 
        // channelLoad: current total dataSize
        // channelWorstPriority: the highest (worst) priority among streams assigned (if any);
        // if channel is empty, set it to Integer.MAX_VALUE.
        class Channel {
            int load;
            int worstPriority; // highest numeric value among assigned streams
            List<Stream> streams;

            Channel() {
                load = 0;
                worstPriority = Integer.MAX_VALUE;
                streams = new ArrayList<>();
            }

            // Check if new stream can be assigned according to priority inversion rules.
            boolean canAccept(Stream s) {
                // If channel is empty, any stream can be assigned.
                if (streams.isEmpty()) {
                    return true;
                }
                // Otherwise, the new stream's priority must be strictly higher (i.e. lower integer) than
                // the worst (largest) priority already in the channel.
                return s.getPriority() < worstPriority;
            }

            // Check if capacity allows the new stream.
            boolean hasCapacity(Stream s, int capacity) {
                return (load + s.getDataSize()) <= capacity;
            }

            void addStream(Stream s) {
                streams.add(s);
                load += s.getDataSize();
                // Update worstPriority: maximum of current worstPriority and new stream's priority;
                // if channel was empty, worstPriority is s.getPriority(), else, it remains max.
                worstPriority = Math.max(worstPriority, s.getPriority());
            }
        }

        // Initialize channels.
        List<Channel> channels = new ArrayList<>();
        for (int i = 0; i < numChannels; i++) {
            channels.add(new Channel());
        }

        // Remove streams which individually exceed channelCapacity.
        List<Stream> validStreams = new ArrayList<>();
        for (Stream s : streams) {
            if (s.getDataSize() <= channelCapacity) {
                validStreams.add(s);
            }
        }

        // Sort streams by priority ascending (i.e. higher importance first).
        // In case of tie in priority, sort by dataSize descending, to assign larger streams earlier.
        validStreams.sort(new Comparator<Stream>() {
            public int compare(Stream s1, Stream s2) {
                if (s1.getPriority() != s2.getPriority()) {
                    return Integer.compare(s1.getPriority(), s2.getPriority());
                }
                return Integer.compare(s2.getDataSize(), s1.getDataSize());
            }
        });

        // Greedy assignment: for each stream, assign to the eligible channel with minimum load.
        for (Stream s : validStreams) {
            int chosenChannel = -1;
            int minLoad = Integer.MAX_VALUE;

            for (int i = 0; i < channels.size(); i++) {
                Channel c = channels.get(i);
                if (c.canAccept(s) && c.hasCapacity(s, channelCapacity)) {
                    if (c.load < minLoad) {
                        minLoad = c.load;
                        chosenChannel = i;
                    }
                }
            }
            if (chosenChannel != -1) {
                channels.get(chosenChannel).addStream(s);
                assignment.put(s.getStreamId(), chosenChannel);
            }
        }

        return assignment;
    }
}