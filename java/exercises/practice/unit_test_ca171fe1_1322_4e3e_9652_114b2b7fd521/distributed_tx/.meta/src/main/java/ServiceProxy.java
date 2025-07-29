public class ServiceProxy {

    public static String prepare(String service, String operationDetails) {
        // If operationDetails contains "fail", simulate an abort.
        if (operationDetails != null && operationDetails.contains("fail")) {
            return "abort";
        }
        return "prepared";
    }

    public static String commit(String service, String txid) {
        // Simulate commit by returning a committed message.
        return "committed";
    }

    public static String abort(String service, String txid) {
        // Simulate abort by returning an aborted message.
        return "aborted";
    }
}