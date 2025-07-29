public class Operation {
    public enum Type {
        PUT,
        DELETE
    }
    
    private final Type type;
    private final String key;
    private final String value;

    public Operation(Type type, String key, String value) {
        this.type = type;
        this.key = key;
        this.value = value;
    }

    public Type getType() {
        return type;
    }

    public String getKey() {
        return key;
    }

    public String getValue() {
        return value;
    }
}