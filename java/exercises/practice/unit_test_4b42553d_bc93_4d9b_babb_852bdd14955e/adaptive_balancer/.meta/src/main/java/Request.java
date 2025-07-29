public class Request {
    private String id;
    private Priority priority;

    public Request(String id, Priority priority) {
        this.id = id;
        this.priority = priority;
    }

    public String getId() {
        return id;
    }

    public Priority getPriority() {
        return priority;
    }
}