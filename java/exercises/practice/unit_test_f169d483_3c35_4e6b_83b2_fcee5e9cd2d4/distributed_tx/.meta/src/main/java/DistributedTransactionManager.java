import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;
import java.util.UUID;

public class DistributedTransactionManager {

    private final int retryCount;
    private final int timeoutMillis;
    private final String logFilePath;

    public DistributedTransactionManager() {
        // Default configuration: 3 retries, 1000ms timeout, log file at dtm.log
        this.retryCount = 3;
        this.timeoutMillis = 1000;
        this.logFilePath = "dtm.log";
    }

    public DistributedTransactionManager(int retryCount, int timeoutMillis, String logFilePath) {
        this.retryCount = retryCount;
        this.timeoutMillis = timeoutMillis;
        this.logFilePath = logFilePath;
    }

    public TransactionResult executeTransaction(List<String> serviceUrls) {
        String transactionId = UUID.randomUUID().toString();
        log("Transaction " + transactionId + " started with " + serviceUrls.size() + " services.");
        boolean prepareSuccess = true;

        // Phase 1: Prepare phase
        for (String baseUrl : serviceUrls) {
            String url = baseUrl + "/prepare/" + transactionId;
            int responseCode = sendRequestWithRetries(url);
            log("Prepare phase: Called " + url + " got response code: " + responseCode);
            if (responseCode != 200) {
                prepareSuccess = false;
            }
        }

        if (!prepareSuccess) {
            log("Transaction " + transactionId + " prepare phase failed. Initiating rollback.");
            // Rollback phase for all services regardless of individual prepare status.
            for (String baseUrl : serviceUrls) {
                String url = baseUrl + "/rollback/" + transactionId;
                int responseCode = sendRequestWithRetries(url);
                log("Rollback: Called " + url + " got response code: " + responseCode);
            }
            log("Transaction " + transactionId + " completed with failure.");
            return new TransactionResult(false, "Prepare phase failed, transaction rolled back.");
        }

        // Phase 2: Commit phase
        boolean commitSuccess = true;
        for (String baseUrl : serviceUrls) {
            String url = baseUrl + "/commit/" + transactionId;
            int responseCode = sendRequestWithRetries(url);
            log("Commit phase: Called " + url + " got response code: " + responseCode);
            if (responseCode != 200) {
                commitSuccess = false;
            }
        }

        if (!commitSuccess) {
            log("Transaction " + transactionId + " commit phase failed. Attempting rollback.");
            // Attempt rollback if commit fails on any service.
            for (String baseUrl : serviceUrls) {
                String url = baseUrl + "/rollback/" + transactionId;
                int responseCode = sendRequestWithRetries(url);
                log("Rollback after commit failure: Called " + url + " got response code: " + responseCode);
            }
            log("Transaction " + transactionId + " completed with failure.");
            return new TransactionResult(false, "Commit phase failed, transaction rolled back.");
        }

        log("Transaction " + transactionId + " completed successfully.");
        return new TransactionResult(true, "Transaction committed successfully.");
    }

    private int sendRequestWithRetries(String requestUrl) {
        int attempt = 0;
        while (attempt < retryCount) {
            try {
                int response = sendHttpRequest(requestUrl);
                if (response == 200) {
                    return response;
                }
            } catch (IOException e) {
                log("IOException on request " + requestUrl + " attempt " + (attempt + 1) + " : " + e.getMessage());
            }
            attempt++;
        }
        return 500;
    }

    private int sendHttpRequest(String requestUrl) throws IOException {
        URL url = new URL(requestUrl);
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setRequestMethod("GET");
        connection.setConnectTimeout(timeoutMillis);
        connection.setReadTimeout(timeoutMillis);
        connection.connect();
        int responseCode = connection.getResponseCode();
        connection.disconnect();
        return responseCode;
    }

    private synchronized void log(String message) {
        try (FileWriter fw = new FileWriter(logFilePath, true);
             PrintWriter pw = new PrintWriter(fw)) {
            pw.println(message);
        } catch (IOException e) {
            // In case of logging failure, output to console.
            System.err.println("Logging failed: " + e.getMessage());
        }
    }
}