package distributed_tx;

public class Operation {
    private final String serviceName;
    private final String detail;
    private final Object data;

    public Operation(String serviceName, String detail, Object data) {
        this.serviceName = serviceName;
        this.detail = detail;
        this.data = data;
    }

    public String getServiceName() {
        return serviceName;
    }

    public String getDetail() {
        return detail;
    }

    public Object getData() {
        return data;
    }
}