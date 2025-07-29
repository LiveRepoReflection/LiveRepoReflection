import java.io.IOException;
import java.net.Socket;
import java.io.OutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

/**
 * Redis-based implementation of RateLimiterStorage.
 * 
 * This is a simplified implementation that communicates directly with Redis using
 * the Redis protocol (RESP). In a real-world scenario, you'd likely use a Redis client
 * library like Jedis, Lettuce, or Redisson.
 */
public class RedisRateLimiterStorage implements RateLimiterStorage {
    private final String redisHost;
    private final int redisPort;
    private Socket socket;
    private OutputStream outputStream;
    private InputStream inputStream;
    
    public RedisRateLimiterStorage(String redisHost, int redisPort) {
        this.redisHost = redisHost;
        this.redisPort = redisPort;
        connect();
    }
    
    private void connect() {
        try {
            socket = new Socket(redisHost, redisPort);
            outputStream = socket.getOutputStream();
            inputStream = socket.getInputStream();
        } catch (IOException e) {
            throw new RuntimeException("Failed to connect to Redis", e);
        }
    }
    
    @Override
    public boolean incrementAndCheckLimit(String clientId, int maxRequests, int timeWindowInSeconds)
            throws DistributedRateLimiterException {
        if (clientId == null || clientId.isEmpty()) {
            throw new DistributedRateLimiterException("Client ID cannot be null or empty");
        }
        if (maxRequests <= 0) {
            throw new DistributedRateLimiterException("Max requests must be greater than zero");
        }
        if (timeWindowInSeconds <= 0) {
            throw new DistributedRateLimiterException("Time window must be greater than zero");
        }
        
        String key = "rate_limit:" + clientId + ":" + timeWindowInSeconds;
        
        try {
            // Check if the key exists
            sendCommand("EXISTS", key);
            boolean keyExists = readIntegerReply() == 1;
            
            if (!keyExists) {
                // Create a new counter
                sendCommand("SETEX", key, String.valueOf(timeWindowInSeconds), "0");
                readSimpleStringReply();
            }
            
            // Increment the counter and get the new value
            sendCommand("INCR", key);
            long count = readIntegerReply();
            
            // If this is the first request, set the expiration time
            if (count == 1) {
                sendCommand("EXPIRE", key, String.valueOf(timeWindowInSeconds));
                readIntegerReply();
            }
            
            return count <= maxRequests;
        } catch (IOException e) {
            throw new DistributedRateLimiterException("Failed to communicate with Redis", e);
        }
    }
    
    private void sendCommand(String... args) throws IOException {
        StringBuilder command = new StringBuilder();
        command.append("*").append(args.length).append("\r\n");
        
        for (String arg : args) {
            command.append("$").append(arg.getBytes(StandardCharsets.UTF_8).length).append("\r\n");
            command.append(arg).append("\r\n");
        }
        
        outputStream.write(command.toString().getBytes(StandardCharsets.UTF_8));
        outputStream.flush();
    }
    
    private String readLine() throws IOException {
        StringBuilder line = new StringBuilder();
        int c;
        
        while ((c = inputStream.read()) != -1) {
            if (c == '\r') {
                int next = inputStream.read();
                if (next == '\n') {
                    break;
                }
                line.append((char) c);
                line.append((char) next);
            } else {
                line.append((char) c);
            }
        }
        
        return line.toString();
    }
    
    private long readIntegerReply() throws IOException {
        String line = readLine();
        if (line.length() == 0) {
            throw new IOException("Unexpected end of stream");
        }
        
        char type = line.charAt(0);
        if (type == ':') {
            return Long.parseLong(line.substring(1));
        } else if (type == '-') {
            throw new IOException("Redis error: " + line.substring(1));
        } else {
            throw new IOException("Unexpected response type: " + type);
        }
    }
    
    private String readSimpleStringReply() throws IOException {
        String line = readLine();
        if (line.length() == 0) {
            throw new IOException("Unexpected end of stream");
        }
        
        char type = line.charAt(0);
        if (type == '+') {
            return line.substring(1);
        } else if (type == '-') {
            throw new IOException("Redis error: " + line.substring(1));
        } else {
            throw new IOException("Unexpected response type: " + type);
        }
    }
    
    @Override
    public void close() {
        try {
            if (socket != null && !socket.isClosed()) {
                socket.close();
            }
        } catch (IOException e) {
            // Ignore exception on close
        }
    }
}