package distributed_tx;

import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

public class LogUtil {

    private static final String LOG_FILE = "dtm.log";

    public static synchronized void writeLog(String logMessage) {
        try (FileWriter fw = new FileWriter(LOG_FILE, true);
             PrintWriter pw = new PrintWriter(fw)) {
            pw.println(System.currentTimeMillis() + " - " + logMessage);
        } catch (IOException e) {
            System.err.println("Failed to write log: " + e.getMessage());
        }
    }
}